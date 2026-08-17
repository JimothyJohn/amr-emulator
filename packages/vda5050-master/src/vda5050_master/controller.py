"""The programmable dispatcher: missions in, tracked order lifecycles out.

``MissionController.submit()`` queues a :class:`~.missions.Mission` for a
robot (chosen explicitly or assigned to the least-busy online robot) and
returns a :class:`MissionRun` whose status walks

    QUEUED -> DISPATCHED -> RUNNING -> COMPLETED | FAILED | CANCELED

Per robot, missions execute strictly in submission order. The controller
handles the whole order lifecycle the way the acceptance process defines it:

- **acceptance vs rejection** is decided from the robot's state — either it
  adopts our orderId, or an error appears whose errorReferences carry our
  orderId (matching on references, never on the wire errorType, because on
  2.x five distinct rejections all share "orderError");
- **base extension**: with ``release=<n>`` the robot gets ``n`` waypoints as
  released base and the rest as horizon; each time it reaches the decision
  point (or asks via ``newBaseRequest``), a stitched update releases the
  next ``n``;
- **completion** is the spec's definition, keyed off the same fields the
  robot drains: our orderId, empty ``nodeStates``/``edgeStates``, and every
  mission action in a final status (any FAILED action fails the run);
- **cancellation** sends the ``cancelOrder`` instant action and awaits
  its verdict; a still-queued run is simply withdrawn;
- **rejections** optionally retry with a fresh orderId (a rejected orderId
  is burned: re-sending it would need a higher orderUpdateId and a stitch
  point that does not exist);
- a robot reporting OFFLINE/CONNECTIONBROKEN mid-run fails the run — the
  broker's last-will mechanism makes that signal trustworthy.
"""

from __future__ import annotations

import asyncio
import contextlib
import enum
from dataclasses import dataclass
from dataclasses import field as dataclass_field

from .fleet import FleetMaster, RobotHandle, errors_referencing, find_action
from .missions import Mission

_FINAL_ACTION = ("FINISHED", "FAILED")
# RETRIABLE (3.0) is not final: the robot idles until a retry/skipRetry
# verdict arrives, and the order cannot complete around it. The controller
# treats it as "needs a decision" and, absent a human, decides skipRetry.
_SETTLED_ACTION = ("FINISHED", "FAILED", "RETRIABLE")


class MissionStatus(enum.Enum):
    QUEUED = "QUEUED"
    DISPATCHED = "DISPATCHED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


FINAL_STATUSES = frozenset({MissionStatus.COMPLETED, MissionStatus.FAILED, MissionStatus.CANCELED})


@dataclass
class MissionRun:
    """One submission of a mission to one robot, trackable to its end."""

    mission: Mission
    robot_serial: str
    release: int | None
    retries: int
    timeout: float
    status: MissionStatus = MissionStatus.QUEUED
    order_id: str = ""
    failure: str = ""
    errors: list[dict] = dataclass_field(default_factory=list)
    final_state: dict | None = None
    _done: asyncio.Event = dataclass_field(default_factory=asyncio.Event)
    _cancel: asyncio.Event = dataclass_field(default_factory=asyncio.Event)

    @property
    def done(self) -> bool:
        return self.status in FINAL_STATUSES

    async def wait(self, timeout: float | None = None) -> MissionStatus:
        """Block until the run reaches a final status and return it."""
        await asyncio.wait_for(self._done.wait(), timeout)
        return self.status

    def _finish(self, status: MissionStatus, failure: str = "") -> None:
        self.status = status
        self.failure = failure
        self._done.set()


class MissionController:
    """Per-robot FIFO mission queues over a :class:`FleetMaster`."""

    def __init__(self, fleet: FleetMaster) -> None:
        self.fleet = fleet
        self.runs: list[MissionRun] = []
        self._queues: dict[str, asyncio.Queue[MissionRun]] = {}
        self._workers: dict[str, asyncio.Task] = {}

    def submit(
        self,
        mission: Mission,
        *,
        robot: str | None = None,
        release: int | None = None,
        retries: int = 0,
        timeout: float = 30.0,
    ) -> MissionRun:
        """Queue a mission; returns immediately with its trackable run.

        ``robot`` is a serial number; without one the least-busy online
        robot is assigned at submission time. ``release`` enables the
        base/horizon strategy (waypoints released per step; default: the
        whole mission at once). ``timeout`` bounds each lifecycle wait —
        dispatch-to-acceptance, progress between decision points, and
        settling — not the whole run.
        """
        serial = robot or self._least_busy_serial()
        run = MissionRun(
            mission=mission,
            robot_serial=serial,
            release=release,
            retries=retries,
            timeout=timeout,
        )
        self.runs.append(run)
        self._queue_for(serial).put_nowait(run)
        return run

    async def cancel(self, run: MissionRun) -> None:
        """Withdraw a queued run, or cancel a dispatched one on the robot."""
        run._cancel.set()
        if run.status is MissionStatus.QUEUED:
            run._finish(MissionStatus.CANCELED)
            return
        await run.wait()

    async def shutdown(self) -> None:
        for task in self._workers.values():
            task.cancel()
        for task in self._workers.values():
            with contextlib.suppress(asyncio.CancelledError):
                await task
        self._workers.clear()

    # ---------------------------------------------------------------- workers

    def _queue_for(self, serial: str) -> asyncio.Queue[MissionRun]:
        if serial not in self._queues:
            self._queues[serial] = asyncio.Queue()
            self._workers[serial] = asyncio.create_task(self._worker(serial))
        return self._queues[serial]

    def _least_busy_serial(self) -> str:
        online = [h for h in self.fleet.robots.values() if h.online]
        if not online:
            raise LookupError("no online robots discovered to assign the mission to")

        def load(handle: RobotHandle) -> tuple[int, str]:
            serial = handle.serial_number
            queued = self._queues[serial].qsize() if serial in self._queues else 0
            active = sum(1 for run in self.runs if run.robot_serial == serial and not run.done)
            return (queued + active, serial)

        return min(online, key=load).serial_number

    async def _worker(self, serial: str) -> None:
        queue = self._queues[serial]
        while True:
            run = await queue.get()
            if run.done:  # withdrawn while queued
                continue
            try:
                await self._execute(run)
            except TimeoutError as exc:
                run._finish(MissionStatus.FAILED, f"timeout: {exc}")
            except Exception as exc:  # a bug in us must not kill the queue
                run._finish(MissionStatus.FAILED, f"internal error: {exc!r}")

    async def _execute(self, run: MissionRun) -> None:
        handle = self.fleet.robot(run.robot_serial)
        for attempt in range(run.retries + 1):
            run.order_id = run.mission.new_order_id()
            run.status = MissionStatus.DISPATCHED
            outcome = await self._drive(run, handle)
            if outcome == "rejected" and attempt < run.retries:
                continue
            break
        if outcome == "completed":
            run._finish(MissionStatus.COMPLETED)
        elif outcome == "canceled":
            run._finish(MissionStatus.CANCELED)
        elif outcome == "rejected":
            run._finish(MissionStatus.FAILED, "order rejected by the robot")
        # "failed" runs were finished (with a reason) inside _drive.

    async def _drive(self, run: MissionRun, handle: RobotHandle) -> str:
        """One dispatch attempt; returns completed/rejected/canceled/failed."""
        mission, order_id = run.mission, run.order_id
        total = len(mission)
        version = self.fleet.profile.version
        released = run.release or total
        await handle.send_order(mission.order(version=version, order_id=order_id, release=released))

        def verdict(state: dict) -> bool:
            return state.get("orderId") == order_id or bool(errors_referencing(state, order_id))

        state = await self._await_state(run, handle, verdict)
        if state is None:
            return await self._teardown(run, handle)
        rejections = errors_referencing(state, order_id)
        if state.get("orderId") != order_id or rejections:
            run.errors.extend(rejections)
            return "rejected"
        run.status = MissionStatus.RUNNING

        update_id = 0
        while released < total:
            decision_node = mission.waypoints[released - 1].node_id

            def at_decision_point(state: dict, node_id: str = decision_node) -> bool:
                return state.get("orderId") == order_id and (
                    state.get("lastNodeId") == node_id or state.get("newBaseRequest") is True
                )

            state = await self._await_state(run, handle, at_decision_point)
            if state is None:
                return await self._teardown(run, handle)
            previous, released = released, min(released + (run.release or total), total)
            update_id += 1
            await handle.send_order(
                mission.update(
                    version=version,
                    order_id=order_id,
                    order_update_id=update_id,
                    previous_release=previous,
                    release=released,
                )
            )

        def settled(state: dict) -> bool:
            if state.get("orderId") != order_id:
                return False
            if state.get("nodeStates") or state.get("edgeStates"):
                return False
            return all(
                find_action(state, action_id, _SETTLED_ACTION) is not None
                for action_id in mission.action_ids
            )

        state = await self._await_state(run, handle, settled)
        if state is None:
            return await self._teardown(run, handle)
        state = await self._resolve_retriable(run, handle, state)
        if state is None:
            return await self._teardown(run, handle)
        run.final_state = state
        failed = [
            entry
            for action_id in mission.action_ids
            if (entry := find_action(state, action_id, ("FAILED",))) is not None
        ]
        if failed:
            run.errors.extend(failed)
            run._finish(
                MissionStatus.FAILED,
                "mission actions failed: "
                + ", ".join(sorted(e.get("actionId", "?") for e in failed)),
            )
            return "failed"
        return "completed"

    async def _resolve_retriable(
        self, run: MissionRun, handle: RobotHandle, state: dict
    ) -> dict | None:
        """Give up on RETRIABLE mission actions via ``skipRetry``.

        The robot idles on a RETRIABLE action until fleet control decides
        retry-or-skip; with no human in the loop the controller decides
        skip, which turns the action FAILED and lets the order settle —
        the failure then fails the run through the normal path.
        """
        stuck = [
            action_id
            for action_id in run.mission.action_ids
            if find_action(state, action_id, ("RETRIABLE",)) is not None
        ]
        if not stuck:
            return state
        for action_id in stuck:
            await handle.send_instant_action("skipRetry", parameters={"actionId": action_id})

        def all_final(state: dict) -> bool:
            return state.get("orderId") == run.order_id and all(
                find_action(state, action_id, _FINAL_ACTION) is not None
                for action_id in run.mission.action_ids
            )

        return await self._await_state(run, handle, all_final)

    async def _teardown(self, run: MissionRun, handle: RobotHandle) -> str:
        """A wait ended early: robot offline, or cancellation requested."""
        if not run._cancel.is_set():
            run._finish(
                MissionStatus.FAILED,
                f"robot went {handle.connection_state or 'silent'} mid-mission",
            )
            return "failed"
        verdict = await handle.cancel_order(timeout=run.timeout)
        if verdict.get("actionStatus") != "FINISHED":
            run.errors.append(verdict)
        return "canceled"

    async def _await_state(
        self,
        run: MissionRun,
        handle: RobotHandle,
        predicate,
    ) -> dict | None:
        """Await a state matching ``predicate``, racing cancel and offline.

        Returns the state, or ``None`` when the run was canceled or the
        robot left ONLINE (check ``run._cancel`` to tell which). Timeouts
        propagate as ``TimeoutError``.
        """
        state_task = asyncio.create_task(
            handle.next_state(predicate, timeout=run.timeout, past=False)
        )
        cancel_task = asyncio.create_task(run._cancel.wait())
        offline_task = asyncio.create_task(
            handle.next_message(
                "connections",
                lambda doc: doc.get("connectionState") not in (None, "ONLINE"),
                timeout=run.timeout + 1,
                past=False,
            )
        )
        tasks = (state_task, cancel_task, offline_task)
        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        if state_task.done() and not state_task.cancelled():
            exc = state_task.exception()
            if exc is not None:
                if run._cancel.is_set():
                    return None
                raise exc
            return state_task.result()
        return None
