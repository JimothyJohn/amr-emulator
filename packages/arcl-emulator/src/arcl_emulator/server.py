"""ARCL (Advanced Robotics Command Language) emulator server.

Emulates the telnet/TCP command interface of Omron LD/HD mobile robots
(ARAM) and the Fleet Manager (Enterprise Manager) queuing surface, per the
official reference manual I617-E-02 — see ``specs/registry.json`` for
provenance and ``specs/arcl_commands.json`` for the per-command manual pages.

One asyncio TCP server; password login; line-based commands; asynchronous
``QueueUpdate:``/``Fault:`` broadcasts to every connected client, exactly the
integration surface a WMS/MES uses against a real fleet. The simulation is
deterministic on simulated time: one virtual AMR drives between named goals
at a fixed speed, drains battery, docks/undocks, and walks queued jobs
through the documented status/substatus lifecycle (manual pages 44-45, 217+).

Everything non-standard lives behind the ``emulator`` command (fault
injection: battery, e-stop, teleport, time scale) and is clearly marked.
"""

from __future__ import annotations

import asyncio
import time as _time
from dataclasses import dataclass
from datetime import UTC, datetime

DEFAULT_PORT = 7171
DEFAULT_PASSWORD = "adept"  # noqa: S105 — the factory-style default, printed at startup

# Default map: goal name -> (x_mm, y_mm, heading_deg). Distances are of
# realistic warehouse scale so drive times are meaningful.
DEFAULT_GOALS = {
    "Goal1": (5000, 0, 0),
    "Goal2": (5000, 5000, 90),
    "Goal3": (0, 5000, 180),
    "Standby": (0, 0, 0),
    "Dock1": (-2000, 0, 180),
}
DEFAULT_ROUTES = ("Loop", "PatrolA")

SPEED_MM_S = 900.0
IDLE_DRAIN_PCT_S = 0.0005
DRIVE_DRAIN_PCT_S = 0.004
CHARGE_GAIN_PCT_S = 0.05

HELP_LINES = [
    ("applicationFaultClear", "Clears an application fault [afc]"),
    ("applicationFaultQuery", "Gets the list of any application faults currently triggered [afq]"),
    ("applicationFaultSet", "Sets an application fault [afs]"),
    ("arclSendText", "Sends the given message to all ARCL clients"),
    ("dock", "Sends the robot to the dock"),
    ("echo", "with no args gets echo, with args sets echo"),
    ("faultsGet", "Gets the list of any faults currently triggered [fg]"),
    ("getDateTime", "gets the date and time"),
    ("getGoals", "gets a list of goals in the map (for use with goto)"),
    ("getRoutes", "gets a list of routes in the map"),
    ("odometer", "shows the robot trip odometer"),
    ("odometerReset", "resets the robot trip odometer"),
    ("oneLineStatus", "gets the status of the robot on one line"),
    ("queueCancel", "cancels queue items by type and value [qc]"),
    ("queuePickup", "queues a pickup request [qp]"),
    ("queuePickupDropoff", "queues a pickup and dropoff request [qpd]"),
    ("queueQuery", "queries the queue by type and value [qq]"),
    ("queueShow", "shows the queue [qs]"),
    ("quit", "closes this connection"),
    ("say", "says the given string"),
    ("status", "gets the status of the robot"),
    ("stop", "stops the robot"),
    ("undock", "undocks the robot"),
    ("emulator", "NON-STANDARD emulator controls (battery/estop/teleport/timescale)"),
]

SHORTCUTS = {
    "qp": "queuepickup",
    "qpd": "queuepickupdropoff",
    "qq": "queuequery",
    "qs": "queueshow",
    "qc": "queuecancel",
    "afs": "applicationfaultset",
    "afc": "applicationfaultclear",
    "afq": "applicationfaultquery",
    "fg": "faultsget",
}


def _fmt_dt(epoch: float) -> tuple[str, str]:
    dt = datetime.fromtimestamp(epoch, tz=UTC)
    return dt.strftime("%m/%d/%Y"), dt.strftime("%H:%M:%S")


@dataclass
class Job:
    item_id: str  # PICKUPn / DROPOFFn
    job_id: str
    priority: int
    goal: str
    kind: str  # "pickup" | "dropoff"
    status: str = "Pending"
    substatus: str = "None"
    robot: str = "none"
    queued_at: float = 0.0
    completed_at: float | None = None
    failed_count: int = 0
    linked_after: str | None = None  # dropoff waits for this pickup item id

    def update_line(self) -> str:
        qd, qt = _fmt_dt(self.queued_at)
        if self.completed_at is None:
            cd = ct = "None"
        else:
            cd, ct = _fmt_dt(self.completed_at)
        robot = f'"{self.robot}"' if self.robot != "none" else "none"
        return (
            f"QueueUpdate: {self.item_id} {self.job_id} {self.priority} "
            f'{self.status} {self.substatus} Goal "{self.goal}" {robot} '
            f"{qd} {qt} {cd} {ct} {self.failed_count}"
        )

    def query_line(self, echo_string: str = "None") -> str:
        qd, qt = _fmt_dt(self.queued_at)
        if self.completed_at is None:
            cd = ct = "None"
        else:
            cd, ct = _fmt_dt(self.completed_at)
        robot = f'"{self.robot}"' if self.robot != "none" else "none"
        return (
            f"QueueQuery: {self.item_id} {self.job_id} {self.priority} "
            f'{self.status} {self.substatus} Goal "{self.goal}" {robot} '
            f"{qd} {qt} {cd} {ct} {echo_string} {self.failed_count}"
        )


class Sim:
    """The one virtual AMR plus the fleet job queue, on simulated time."""

    def __init__(
        self,
        *,
        robot_name: str = "Sim_LD90",
        start_epoch: float | None = None,
        time_scale: float = 1.0,
    ) -> None:
        self.robot_name = robot_name
        self.goals = dict(DEFAULT_GOALS)
        self.routes = list(DEFAULT_ROUTES)
        self.x, self.y, self.heading = 0.0, 0.0, 0.0
        self.battery = 100.0
        self.temperature = 34
        self.localization_score = 0.988
        self.status_text = "Available"
        self.docking_state = "Undocked"
        self.charge_state = "Not"
        self.estop = False
        self.echo_default = True
        self.time_scale = time_scale
        self._epoch = start_epoch if start_epoch is not None else _time.time()
        self._mono = _time.monotonic()
        self.odometer_mm = 0.0
        self.odometer_deg = 0.0
        self.odometer_start = self.now()
        self.jobs: list[Job] = []
        self._pickup_seq = 0
        self._dropoff_seq = 0
        self._job_seq = 0
        self.app_faults: dict[str, tuple[str, str]] = {}  # name -> (fault_id, short_desc)
        self.broadcast = lambda line: None  # wired by the server

    def now(self) -> float:
        return self._epoch + (_time.monotonic() - self._mono) * self.time_scale

    def set_time_scale(self, scale: float) -> None:
        self._epoch = self.now()
        self._mono = _time.monotonic()
        self.time_scale = scale

    # ------------------------------------------------------------- queueing

    def queue_pickup(self, goal: str, priority: int, job_id: str | None) -> Job:
        self._pickup_seq += 1
        job = Job(
            item_id=f"PICKUP{self._pickup_seq}",
            job_id=job_id or self._auto_job_id(),
            priority=priority,
            goal=goal,
            kind="pickup",
            queued_at=self.now(),
        )
        self.jobs.append(job)
        self.broadcast(job.update_line())
        return job

    def queue_dropoff(self, goal: str, priority: int, job_id: str, after: str | None) -> Job:
        self._dropoff_seq += 1
        job = Job(
            item_id=f"DROPOFF{self._dropoff_seq}",
            job_id=job_id,
            priority=priority,
            goal=goal,
            kind="dropoff",
            queued_at=self.now(),
            linked_after=after,
        )
        if after is not None:
            job.substatus = f"ID_{after}"
        self.jobs.append(job)
        self.broadcast(job.update_line())
        return job

    def _auto_job_id(self) -> str:
        self._job_seq += 1
        return f"JOB{self._job_seq}"

    def cancel(self, kind: str, value: str, reason: str | None) -> list[Job]:
        cancelled = []
        for job in self.jobs:
            if job.status in ("Completed", "Cancelled"):
                continue
            match = (
                (kind == "id" and job.item_id == value)
                or (kind == "jobid" and job.job_id == value)
                or (kind == "robotname" and job.robot == value)
                or (kind == "status" and job.status.lower() == value.lower())
            )
            if match:
                job.status = "Cancelled"
                job.substatus = reason or "None"
                job.completed_at = self.now()
                self.broadcast(job.update_line())
                cancelled.append(job)
        if any(j.status == "Cancelled" and j.robot != "none" for j in cancelled):
            self.status_text = "Available"
        return cancelled

    def _next_job(self) -> Job | None:
        candidates = [j for j in self.jobs if j.status == "Pending" and self._runnable(j)]
        if not candidates:
            return None
        return sorted(candidates, key=lambda j: (-j.priority, j.queued_at))[0]

    def _runnable(self, job: Job) -> bool:
        if job.linked_after is None:
            return True
        linked = next((j for j in self.jobs if j.item_id == job.linked_after), None)
        return linked is None or linked.status == "Completed"

    # ------------------------------------------------------------ simulation

    async def run(self) -> None:
        # Wall-clock pacing floor keeps high time scales from busy-looping
        # the event loop; the simulated step grows instead.
        while True:
            wall = max(0.005, 0.1 / self.time_scale)
            await asyncio.sleep(wall)
            self._advance(wall * self.time_scale)

    def _advance(self, dt: float) -> None:
        drain = DRIVE_DRAIN_PCT_S if self.status_text.startswith("Going to") else IDLE_DRAIN_PCT_S
        if self.docking_state == "Docked":
            self.battery = min(100.0, self.battery + CHARGE_GAIN_PCT_S * dt)
            self.charge_state = "Not" if self.battery >= 100.0 else "Bulk"
        else:
            self.battery = max(0.0, self.battery - drain * dt)
        if self.estop:
            return
        active = next((j for j in self.jobs if j.status == "InProgress"), None)
        if active is None:
            job = self._next_job()
            if job is not None:
                job.status = "InProgress"
                job.robot = self.robot_name
                for sub in ("UnAllocated", "Allocated"):
                    job.substatus = sub
                    self.broadcast(job.update_line())
                job.substatus = "BeforePickup" if job.kind == "pickup" else "BeforeDropoff"
                self.broadcast(job.update_line())
                job.substatus = "Driving"
                self.broadcast(job.update_line())
                self.status_text = f"Going to {job.goal}"
                if self.docking_state == "Docked":
                    self.docking_state = "Undocked"
                    self.charge_state = "Not"
            return
        if active.goal not in self.goals:
            active.status = "Cancelled"
            active.substatus = "None"
            active.completed_at = self.now()
            self.broadcast(active.update_line())
            self.status_text = "Available"
            return
        tx, ty, th = self.goals[active.goal]
        dx, dy = tx - self.x, ty - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        step = SPEED_MM_S * dt
        if dist <= step:
            self.x, self.y, self.heading = float(tx), float(ty), float(th)
            self.odometer_mm += dist
            active.substatus = "AfterPickup" if active.kind == "pickup" else "AfterDropoff"
            self.broadcast(active.update_line())
            active.status = "Completed"
            active.substatus = "None"
            active.completed_at = self.now()
            self.broadcast(active.update_line())
            self.status_text = f"Arrived at {active.goal}"
        else:
            self.x += dx / dist * step
            self.y += dy / dist * step
            self.odometer_mm += step
