"""A MassRobotics AMR Interop Standard robot (sender side).

The standard's robot role is a WebSocket client that connects to a receiver,
sends one identityReport, then streams statusReports. Vecna Robotics' fleet
(APT, ATG, AFL, CPJ) is AMR Interop certified, so this emulator ships Vecna
presets front and center; any other identity is a config away.

The movement model is deliberately simple — straight-line travel at
``max_speed`` toward the current destination — but honest about the wire:
every message is validated against the vendored official schema before it
leaves, and the path/destinations arrays carry real predictions from the
same model that moves the robot.
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import math
import uuid as uuid_module
from dataclasses import dataclass, field

from vda5050_emulator.clock import SimClock, iso

from . import ws
from .validation import validate_outgoing

# Default planar datum: the standard identifies maps by UUID; one fixed,
# lowercase UUID is this emulator's "facility map" unless configured.
DEFAULT_PLANAR_DATUM = "4b8302da-21ad-401f-af45-1dfd956b80b5"

OPERATIONAL_STATES = frozenset(
    {
        "navigating",
        "idle",
        "disabled",
        "offline",
        "charging",
        "waitingHumanEvent",
        "waitingExternalEvent",
        "waitingInternalEvent",
        "manualOverride",
    }
)


@dataclass(frozen=True)
class AMRConfig:
    """Identity and physics for one emulated AMR."""

    manufacturer_name: str = "Vecna Robotics"
    robot_model: str = "APT"
    robot_serial_number: str = "APT-0001"
    envelope_x: float = 2.4
    envelope_y: float = 1.0
    max_speed: float = 2.0  # m/s
    max_run_time: float = 8.0  # hours on a full charge
    battery_percentage: float = 100.0
    status_interval: float = 1.0  # seconds between statusReports
    planar_datum: str = DEFAULT_PLANAR_DATUM
    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0  # radians, world frame
    identity_extras: dict = field(default_factory=dict)

    @property
    def uuid(self) -> str:
        """Stable per-robot UUID, derived exactly like the reference client
        (md5 over manufacturer+serial) — deterministic across reconnects,
        and lowercase because the schema's uuid patterns reject uppercase."""
        digest = hashlib.md5(  # noqa: S324 - identity derivation, not security
            (self.manufacturer_name + self.robot_serial_number).encode()
        ).hexdigest()
        return str(uuid_module.UUID(digest))


# Vecna's current fleet, per vecnarobotics.com marketing pages. Envelope and
# speed values are emulator defaults in the right ballpark for each vehicle
# class, not published vendor specs — override via AMRConfig for fidelity.
VECNA_MODELS: dict[str, dict] = {
    "APT": {"robot_model": "APT", "envelope_x": 2.4, "envelope_y": 1.0, "max_speed": 2.0},
    "ATG": {"robot_model": "ATG", "envelope_x": 1.8, "envelope_y": 0.9, "max_speed": 2.0},
    "AFL": {"robot_model": "AFL", "envelope_x": 2.6, "envelope_y": 1.2, "max_speed": 1.8},
    "CPJ": {"robot_model": "CPJ", "envelope_x": 1.7, "envelope_y": 0.8, "max_speed": 1.6},
}


def vecna_config(model: str = "APT", serial_number: str | None = None, **overrides) -> AMRConfig:
    """An AMRConfig for one of Vecna's certified vehicles (APT/ATG/AFL/CPJ)."""
    if model not in VECNA_MODELS:
        raise KeyError(f"unknown Vecna model {model!r}; choose from {sorted(VECNA_MODELS)}")
    settings: dict = {
        "manufacturer_name": "Vecna Robotics",
        **VECNA_MODELS[model],
        "robot_serial_number": serial_number or f"{model}-0001",
    }
    settings.update(overrides)
    return AMRConfig(**settings)


def _quaternion(heading: float) -> dict:
    """Planar heading as the schema's required quaternion (yaw about z)."""
    return {
        "x": 0.0,
        "y": 0.0,
        "z": round(math.sin(heading / 2), 6),
        "w": round(math.cos(heading / 2), 6),
    }


class MassRoboticsAMR:
    """One emulated robot streaming interop reports to a receiver."""

    def __init__(self, config: AMRConfig | None = None, *, clock: SimClock | None = None) -> None:
        self.config = config or AMRConfig()
        self.clock = clock or SimClock()
        self.x = self.config.x
        self.y = self.config.y
        self.heading = self.config.heading
        self.battery_percentage = self.config.battery_percentage
        self.charging = False
        self.error_codes: list[str] = []
        self.manual_state: str | None = None  # overrides the derived state
        self.sent: int = 0  # statusReports delivered
        self._destination: tuple[float, float] | None = None
        self._arrived = asyncio.Event()
        self._arrived.set()
        self._socket: ws.WebSocket | None = None
        self._task: asyncio.Task | None = None
        self._last_tick: float | None = None

    # -- lifecycle -------------------------------------------------------

    async def start(self, uri: str) -> None:
        """Connect, deliver the identityReport, and start the status stream."""
        self._socket = await ws.connect(uri)
        identity = self.identity_report()
        validate_outgoing(identity, "identityReport")
        await self._socket.send_text(_dumps(identity))
        self._task = asyncio.create_task(self._status_loop())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
        if self._socket is not None:
            await self._socket.close()
            self._socket = None

    # -- commands --------------------------------------------------------

    def navigate_to(self, x: float, y: float) -> None:
        self._destination = (x, y)
        self._arrived = asyncio.Event()

    async def wait_for_arrival(self, timeout: float = 60.0) -> None:
        await asyncio.wait_for(self._arrived.wait(), timeout)

    def set_charging(self, charging: bool) -> None:
        self.charging = charging

    def set_error(self, code: str) -> None:
        if code not in self.error_codes:
            self.error_codes.append(code)

    def clear_errors(self) -> None:
        self.error_codes.clear()

    def override_state(self, state: str | None) -> None:
        """Pin operationalState (e.g. ``manualOverride``); None resumes."""
        if state is not None and state not in OPERATIONAL_STATES:
            raise ValueError(f"not an operationalState from the standard: {state!r}")
        self.manual_state = state

    # -- report bodies ---------------------------------------------------

    def identity_report(self) -> dict:
        report = {
            "uuid": self.config.uuid,
            "timestamp": iso(self.clock.time()),
            "manufacturerName": self.config.manufacturer_name,
            "robotModel": self.config.robot_model,
            "robotSerialNumber": self.config.robot_serial_number,
            "baseRobotEnvelope": {"x": self.config.envelope_x, "y": self.config.envelope_y},
            "maxSpeed": self.config.max_speed,
            "maxRunTime": self.config.max_run_time,
            **self.config.identity_extras,
        }
        return report

    def status_report(self) -> dict:
        speed = self._current_speed()
        report: dict = {
            "uuid": self.config.uuid,
            "timestamp": iso(self.clock.time()),
            "operationalState": self.operational_state(),
            "location": {
                "x": round(self.x, 4),
                "y": round(self.y, 4),
                "angle": _quaternion(self.heading),
                "planarDatum": self.config.planar_datum,
            },
            "velocity": {"linear": round(speed, 4)},
            "batteryPercentage": round(self.battery_percentage, 2),
            "remainingRunTime": round(
                self.config.max_run_time * self.battery_percentage / 100.0, 3
            ),
        }
        if self.error_codes:
            # "should be omitted for normal operation"
            report["errorCodes"] = list(self.error_codes)
        if self._destination is not None:
            report["destinations"] = [self._predicted(*self._destination, self._eta())]
            report["path"] = self._path_prediction()
        return report

    def operational_state(self) -> str:
        if self.manual_state is not None:
            return self.manual_state
        if self.error_codes:
            return "disabled"
        if self.charging:
            return "charging"
        if self._destination is not None:
            return "navigating"
        return "idle"

    # -- internals -------------------------------------------------------

    def _current_speed(self) -> float:
        moving = self._destination is not None and self.operational_state() == "navigating"
        return self.config.max_speed if moving else 0.0

    def _eta(self) -> float:
        assert self._destination is not None
        distance = math.dist((self.x, self.y), self._destination)
        return self.clock.time() + distance / self.config.max_speed

    def _predicted(self, x: float, y: float, when: float) -> dict:
        return {
            "timestamp": iso(when),
            "x": round(x, 4),
            "y": round(y, 4),
            "angle": _quaternion(self.heading),
            "planarDatumUUID": self.config.planar_datum,
        }

    def _path_prediction(self) -> list[dict]:
        """Up to 10 one-second-spaced points along the remaining line.

        Timestamps differ per entry, satisfying the schema's uniqueItems.
        """
        assert self._destination is not None
        now = self.clock.time()
        points = []
        for step in range(1, 11):
            x, y = self._position_after(step)
            points.append(self._predicted(x, y, now + step))
            if (x, y) == self._destination:
                break
        return points

    def _position_after(self, seconds: float) -> tuple[float, float]:
        assert self._destination is not None
        tx, ty = self._destination
        distance = math.dist((self.x, self.y), (tx, ty))
        reach = self.config.max_speed * seconds
        if reach >= distance:
            return (tx, ty)
        ratio = reach / distance
        return (self.x + (tx - self.x) * ratio, self.y + (ty - self.y) * ratio)

    def _tick(self) -> None:
        """Advance physics to the current clock time."""
        now = self.clock.time()
        if self._last_tick is None:
            self._last_tick = now
            return
        elapsed, self._last_tick = now - self._last_tick, now
        if elapsed <= 0:
            return
        if self._destination is not None and self.operational_state() == "navigating":
            tx, ty = self._destination
            if (self.x, self.y) != (tx, ty):
                self.heading = math.atan2(ty - self.y, tx - self.x)
            self.x, self.y = self._position_after(elapsed)
            if (self.x, self.y) == (tx, ty):
                self._destination = None
                self._arrived.set()
        if self.charging:
            self.battery_percentage = min(100.0, self.battery_percentage + elapsed / 36.0)
        else:
            drain = elapsed / (self.config.max_run_time * 36.0)
            self.battery_percentage = max(0.0, self.battery_percentage - drain)

    async def _status_loop(self) -> None:
        assert self._socket is not None
        while True:
            self._tick()
            report = self.status_report()
            validate_outgoing(report, "statusReport")
            await self._socket.send_text(_dumps(report))
            self.sent += 1
            await self.clock.sleep(self.config.status_interval)


def _dumps(message: dict) -> str:
    return json.dumps(message, separators=(",", ":"))
