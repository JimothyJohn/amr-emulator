"""Action execution engine (sections 6.2 and 6.6.9).

Order/zone actions run through a queue with the blocking semantics of
Figure 11: NONE/SOFT actions are collected for parallel execution, SINGLE/HARD
actions wait for the collected batch and run alone, SOFT/HARD suspend
automatic driving while they are anywhere in the queue. Instant actions start
immediately (their 3.0 blocking type is always NONE; 2.x instant actions may
carry SOFT/HARD, which then also suspends driving).

Handlers implement the predefined actions of Table 4 with the state
transitions of Table 5. A handler drives its own actionState through
INITIALIZING/RUNNING/... via the run object; the engine owns queuing,
cancellation (cancelOrder, order clearing), pausing (startPause), forced
failures (fault injection) and the RETRIABLE/retry/skipRetry cycle.
"""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .robot import VirtualAGV


def params(action: dict) -> dict[str, Any]:
    return {p["key"]: p["value"] for p in action.get("actionParameters", [])}


@dataclass
class ActionRun:
    action: dict
    state: dict  # the actionState dict inside the state message arrays
    origin: str  # "node" | "edge" | "instant" | "zone"
    element_sequence: int = -1  # sequenceId of the triggering node/edge
    task: asyncio.Task | None = None
    trigger_event: asyncio.Event = field(default_factory=asyncio.Event)
    finished_event: asyncio.Event = field(default_factory=asyncio.Event)

    @property
    def action_id(self) -> str:
        return self.action.get("actionId", "")

    @property
    def action_type(self) -> str:
        return self.action.get("actionType", "")

    @property
    def blocking_type(self) -> str:
        return self.action.get("blockingType", "NONE")

    @property
    def status(self) -> str:
        return self.state["actionStatus"]

    @property
    def settled(self) -> bool:
        return self.status in ("FINISHED", "FAILED")

    @property
    def pause_allowed(self) -> bool:
        return self.action_type in ("pick", "drop", "finePositioning")

    @property
    def cancel_allowed(self) -> bool:
        return self.action_type not in ("cancelOrder", "shutdown")


class ActionFailure(Exception):
    """Raised by handlers to fail an action (message goes to actionResult)."""

    def __init__(self, message: str, *, retriable: bool = False) -> None:
        super().__init__(message)
        self.retriable = retriable


class ActionEngine:
    def __init__(self, robot: VirtualAGV) -> None:
        self.robot = robot
        self.queue: deque[ActionRun] = deque()
        self.active: list[ActionRun] = []
        self._runner: asyncio.Task | None = None
        self.changed = asyncio.Event()  # set whenever blocking situation may change

    # -- queries -------------------------------------------------------------

    @property
    def blocks_driving(self) -> bool:
        pending = any(r.blocking_type in ("SOFT", "HARD") for r in self.queue)
        running = any(r.blocking_type in ("SOFT", "HARD") and not r.settled for r in self.active)
        return pending or running

    def find(self, action_id: str) -> ActionRun | None:
        for run in (*self.active, *self.queue):
            if run.action_id == action_id:
                return run
        return None

    # -- lifecycle -----------------------------------------------------------

    def enqueue(self, runs: list[ActionRun]) -> None:
        self.queue.extend(runs)
        self.changed.set()
        if runs and (self._runner is None or self._runner.done()):
            self._runner = asyncio.create_task(self._process_queue())

    def start_instant(self, run: ActionRun) -> None:
        self.active.append(run)
        run.task = asyncio.create_task(self._execute(run))
        self.changed.set()

    async def _process_queue(self) -> None:
        while self.queue:
            run = self.queue.popleft()
            if run.blocking_type in ("SINGLE", "HARD"):
                await self._wait_for_batch()
                self.active.append(run)
                run.task = asyncio.create_task(self._execute(run))
                await run.finished_event.wait()
            else:
                self.active.append(run)
                run.task = asyncio.create_task(self._execute(run))
        self.changed.set()

    async def _wait_for_batch(self) -> None:
        for run in list(self.active):
            if not run.settled and run.status != "RETRIABLE":
                await run.finished_event.wait()

    async def _execute(self, run: ActionRun) -> None:
        robot = self.robot
        forced = robot.forced_action_failures.pop(run.action_type, None) or (
            robot.forced_action_failures.pop(run.action_id, None)
        )
        try:
            if forced is not None:
                raise ActionFailure(
                    f"forced by fault injection: {forced}", retriable=forced == "RETRIABLE"
                )
            handler = HANDLERS.get(run.action_type, _default_handler)
            await handler(robot, run)
            if not run.settled:
                robot.set_action_status(run, "FINISHED")
        except ActionFailure as failure:
            retriable = failure.retriable or bool(run.action.get("retriable", False))
            if retriable and "RETRIABLE" in robot.profile.action_statuses:
                robot.set_action_status(run, "RETRIABLE", result=str(failure))
            else:
                robot.set_action_status(run, "FAILED", result=str(failure))
        except asyncio.CancelledError:
            if not run.settled:
                robot.set_action_status(run, "FAILED", result="cancelled")
        except Exception as exc:  # a handler bug must not kill the robot loop
            robot.set_action_status(run, "FAILED", result=f"internal: {exc!r}")
        finally:
            if run.settled:
                run.finished_event.set()
            self.changed.set()

    async def retry(self, run: ActionRun) -> None:
        if run.status != "RETRIABLE":
            raise ActionFailure(f"action {run.action_id} is not RETRIABLE")
        run.finished_event = asyncio.Event()
        run.task = asyncio.create_task(self._execute(run))

    def cancel_order_actions(self) -> list[ActionRun]:
        """cancelOrder/clearing: scheduled -> FAILED, running cancellable ->
        cancelled, running non-cancellable are left to finish (6.6.7)."""
        outstanding: list[ActionRun] = []
        while self.queue:
            run = self.queue.popleft()
            self.robot.set_action_status(run, "FAILED", result="order cancelled")
            run.finished_event.set()
        for run in list(self.active):
            if run.origin == "instant" or run.settled:
                continue
            if run.status == "RETRIABLE":
                self.robot.set_action_status(run, "FAILED", result="order cancelled")
                run.finished_event.set()
            elif run.cancel_allowed:
                if run.task is not None:
                    run.task.cancel()
                outstanding.append(run)
            else:
                outstanding.append(run)
        self.changed.set()
        return outstanding

    def finish_edge_actions(self, edge_sequence: int) -> None:
        """Leaving an edge finishes the actions the edge triggered (6.6.2)."""
        for run in list(self.active):
            if run.origin == "edge" and run.element_sequence == edge_sequence and not run.settled:
                if run.task is not None:
                    run.task.cancel()
                self.robot.set_action_status(run, "FINISHED", result="edge traversed")
                run.finished_event.set()

    def drop_horizon_states(self, kept: set[str]) -> None:
        self.queue = deque(r for r in self.queue if r.action_id in kept)


# ---------------------------------------------------------------------------
# Handlers. Each receives (robot, run); default: INITIALIZING -> RUNNING for
# the configured duration -> FINISHED (engine sets it).


async def _default_handler(robot: VirtualAGV, run: ActionRun) -> None:
    await robot.action_progress(run, robot.config.action_duration)


async def _start_pause(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    robot.set_paused(True)
    robot.set_action_status(run, "FINISHED")


async def _stop_pause(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    robot.set_paused(False)
    robot.set_action_status(run, "FINISHED")


async def _cancel_order(robot: VirtualAGV, run: ActionRun) -> None:
    await robot.handle_cancel_order(run)


async def _state_request(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    await robot.publish_state(reason="stateRequest")
    robot.set_action_status(run, "FINISHED")


async def _factsheet_request(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    await robot.publish_factsheet()
    robot.set_action_status(run, "FINISHED")


async def _init_position(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    missing = [k for k in ("x", "y", "theta", "mapId", "lastNodeId") if k not in p]
    if missing:
        raise ActionFailure(f"missing parameters: {', '.join(missing)}")
    if robot.profile.has_maps and not robot.map_known(str(p["mapId"])):
        raise ActionFailure(f"unknown mapId {p['mapId']!r}")
    robot.set_action_status(run, "RUNNING")
    robot.teleport(
        x=float(p["x"]),
        y=float(p["y"]),
        theta=float(p["theta"]),
        map_id=str(p["mapId"]),
        last_node_id=str(p["lastNodeId"]),
    )
    robot.set_action_status(run, "FINISHED")


async def _start_charging(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    await robot.clock.sleep(0.5)
    robot.set_charging(True)
    robot.set_action_status(run, "FINISHED")


async def _stop_charging(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    robot.set_charging(False)
    robot.set_action_status(run, "FINISHED")


async def _download_map(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    for key in ("mapId", "mapVersion", "mapDownloadLink"):
        if key not in p:
            raise ActionFailure(f"missing parameter {key}")
    if robot.map_on_robot(str(p["mapId"]), str(p["mapVersion"])):
        robot.report_semantic_error(
            "duplicate_map", {"mapId": str(p["mapId"]), "mapVersion": str(p["mapVersion"])}
        )
        raise ActionFailure("map already on robot")
    robot.set_action_status(run, "RUNNING")
    await robot.action_progress(run, robot.config.download_duration, initializing=False)
    robot.add_map(str(p["mapId"]), str(p["mapVersion"]))
    robot.set_action_status(run, "FINISHED")


async def _enable_map(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    robot.set_action_status(run, "RUNNING")
    if not robot.enable_map(str(p.get("mapId")), str(p.get("mapVersion"))):
        raise ActionFailure("mapId/mapVersion combination not on robot")
    robot.set_action_status(run, "FINISHED")


async def _delete_map(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    robot.set_action_status(run, "RUNNING")
    if not robot.delete_map(str(p.get("mapId")), str(p.get("mapVersion"))):
        raise ActionFailure("map not on robot or currently in use")
    robot.set_action_status(run, "FINISHED")


async def _download_zone_set(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    for key in ("zoneSetId", "zoneSetDownloadLink"):
        if key not in p:
            raise ActionFailure(f"missing parameter {key}")
    robot.set_action_status(run, "RUNNING")
    await robot.action_progress(run, robot.config.download_duration, initializing=False)
    if not robot.zones.add({"zoneSetId": str(p["zoneSetId"]), "mapId": robot.map_id, "zones": []}):
        robot.report_semantic_error("duplicate_zone_set", {"zoneSetId": str(p["zoneSetId"])})
        raise ActionFailure("zone set already on robot")
    robot.touch("zoneSets")
    robot.set_action_status(run, "FINISHED")


async def _enable_zone_set(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    robot.set_action_status(run, "RUNNING")
    if not robot.zones.enable(str(p.get("zoneSetId"))):
        raise ActionFailure("zone set not on robot")
    robot.touch("zoneSets")
    robot.set_action_status(run, "FINISHED")


async def _delete_zone_set(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    robot.set_action_status(run, "RUNNING")
    if not robot.zones.delete(str(p.get("zoneSetId"))):
        raise ActionFailure("zone set not on robot")
    robot.touch("zoneSets")
    robot.set_action_status(run, "FINISHED")


async def _clear_instant_actions(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    robot.set_action_status(run, "FINISHED")
    robot.clear_settled_instant_actions(keep=run.action_id)


async def _clear_zone_actions(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    robot.clear_settled_zone_actions()
    robot.set_action_status(run, "FINISHED")


async def _log_report(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    reason = params(run.action).get("reason", "requested")
    robot.set_action_status(run, "FINISHED", result=f"emulator-log-{run.action_id[:8]} ({reason})")


async def _pick(robot: VirtualAGV, run: ActionRun) -> None:
    if robot.loads:
        raise ActionFailure("load handling device already occupied", retriable=True)
    await robot.action_progress(run, robot.config.pick_duration)
    robot.set_load(params(run.action))
    robot.set_action_status(run, "FINISHED", result="load picked")


async def _drop(robot: VirtualAGV, run: ActionRun) -> None:
    if not robot.loads:
        raise ActionFailure("no load to drop", retriable=True)
    await robot.action_progress(run, robot.config.drop_duration)
    robot.clear_load()
    robot.set_action_status(run, "FINISHED", result="load dropped")


async def _wait_for_trigger(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    await run.trigger_event.wait()
    robot.set_action_status(run, "FINISHED", result="triggered")


async def _trigger(robot: VirtualAGV, run: ActionRun) -> None:
    robot.set_action_status(run, "RUNNING")
    released = robot.release_wait_for_trigger()
    if not released:
        raise ActionFailure("no waitForTrigger action is waiting")
    robot.set_action_status(run, "FINISHED")


async def _retry(robot: VirtualAGV, run: ActionRun) -> None:
    target = robot.engine.find(str(params(run.action).get("actionId", "")))
    if target is None or target.status != "RETRIABLE":
        raise ActionFailure("no RETRIABLE action with that actionId")
    robot.set_action_status(run, "RUNNING")
    await robot.engine.retry(target)
    robot.set_action_status(run, "FINISHED")


async def _skip_retry(robot: VirtualAGV, run: ActionRun) -> None:
    target = robot.engine.find(str(params(run.action).get("actionId", "")))
    if target is None or target.status != "RETRIABLE":
        raise ActionFailure("no RETRIABLE action with that actionId")
    robot.set_action_status(run, "RUNNING")
    robot.set_action_status(target, "FAILED", result="skipped via skipRetry")
    target.finished_event.set()
    robot.set_action_status(run, "FINISHED")


async def _start_hibernation(robot: VirtualAGV, run: ActionRun) -> None:
    await robot.handle_start_hibernation(run, params(run.action).get("wakeUpTime"))


async def _stop_hibernation(robot: VirtualAGV, run: ActionRun) -> None:
    await robot.handle_stop_hibernation(run)


async def _shutdown(robot: VirtualAGV, run: ActionRun) -> None:
    await robot.handle_shutdown(run)


async def _update_certificate(robot: VirtualAGV, run: ActionRun) -> None:
    p = params(run.action)
    for key in ("service", "keyDownloadLink", "certificateDownloadLink"):
        if key not in p:
            raise ActionFailure(f"missing parameter {key}")
    await robot.action_progress(run, robot.config.download_duration)
    robot.set_action_status(run, "FINISHED", result=f"certificates for {p['service']} active")


HANDLERS = {
    "startPause": _start_pause,
    "stopPause": _stop_pause,
    "cancelOrder": _cancel_order,
    "stateRequest": _state_request,
    "factsheetRequest": _factsheet_request,
    "initPosition": _init_position,
    "initializePosition": _init_position,
    "startCharging": _start_charging,
    "stopCharging": _stop_charging,
    "downloadMap": _download_map,
    "enableMap": _enable_map,
    "deleteMap": _delete_map,
    "downloadZoneSet": _download_zone_set,
    "enableZoneSet": _enable_zone_set,
    "deleteZoneSet": _delete_zone_set,
    "clearInstantActions": _clear_instant_actions,
    "clearZoneActions": _clear_zone_actions,
    "logReport": _log_report,
    "pick": _pick,
    "drop": _drop,
    "waitForTrigger": _wait_for_trigger,
    "trigger": _trigger,
    "retry": _retry,
    "skipRetry": _skip_retry,
    "startHibernation": _start_hibernation,
    "stopHibernation": _stop_hibernation,
    "shutdown": _shutdown,
    "updateCertificate": _update_certificate,
}
