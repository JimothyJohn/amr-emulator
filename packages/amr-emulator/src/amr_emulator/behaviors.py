"""Hand-written behavior overlays for endpoints where generic CRUD is too dumb.

Everything not listed here falls back to the spec-driven generic handler in
app.py. Overrides receive a RequestCtx and return (status, body) — or
(status, body, media_type) for non-JSON endpoints.

Mission simulation: queued missions "run" without any background task — the
lifecycle is derived from timestamps at read time (Pending → Executing for
MISSION_DURATION_S seconds → Done, FIFO, one robot). This is what makes the
simulation work identically under uvicorn, Docker, and AWS Lambda (where no
code runs between invocations), and what keeps tests deterministic: freeze
`_now` and the whole world stands still. While a mission executes, /status
reports Executing, the position advances along a patrol loop, the battery
drains, and PUT /status {"state_id": 4} pauses the simulation clock
({"state_id": 3} resumes it).
"""

from __future__ import annotations

import itertools
import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from amr_emulator.examples import example_from_schema, overlay_compatible
from amr_emulator.spec import Operation, Spec
from amr_emulator.state import StateStore

REGISTER_COUNT = 200

# PUT /status choices, identical across every tracked spec (the swagger files
# state them in the property descriptions, not as enums):
#   state_id "Choices are: {3, 4, 11}, State: {Ready, Pause, Manualcontrol}"
#   mode_id  "Choices are: {3, 7}"
#   clear_error "Choices are: {True}"
STATE_CHOICES = {3: "Ready", 4: "Pause", 11: "Manualcontrol"}
MODE_CHOICES = {3: "Mapping", 7: "Mission"}
UPTIME_START_S = 3600  # the emulated robot "booted" an hour before first contact

# --- mission simulation tuning ----------------------------------------------
MISSION_DURATION_S = 10.0  # each mission executes for this long
MISSION_PENDING_LAG_S = 1.0  # a real robot takes a beat to pick a mission up
MISSION_SPEED_M_S = 0.5  # simulated travel speed while executing
BATTERY_START = 92.5
BATTERY_DRAIN_PER_S = 0.05  # percent per executing second
BATTERY_FLOOR = 20.0
BATTERY_SECONDS_PER_PERCENT = 375  # scales battery_time_remaining
CHARGE_RATE_DEFAULT = 0.5  # percent per simulated second while charging
CHARGE_TARGET_DEFAULT = 100.0
LOOP_LENGTH_M = 40.0  # the simulated robot patrols a 40 m loop
POSITION_HOME_X = 5.0
POSITION_HOME_Y = 5.0


def _wall_clock() -> float:
    return time.time()


# The one clock everything reads. A plain reassignable attribute on purpose:
# frozen-clock tests and scenario replay (record.py) substitute it.
_now: Callable[[], float] = _wall_clock


# Values overlaid onto the schema-derived /status example. Only keys that
# exist in the schema (and match its types) are applied — see overlay_compatible.
STATUS_OVERLAY: dict[str, Any] = {
    "robot_name": "MiR_Emulated",
    "robot_model": "MiR250",
    "serial_number": "000000000000000",
    "state_id": 3,
    "state_text": "Ready",
    "mode_id": 7,
    "mode_text": "Mission",
    "battery_percentage": 92.5,
    "battery_time_remaining": 34664,
    "uptime": 3600,
    "mission_text": "Waiting for new missions...",
    "moved": 1204.5,
    "distance_to_next_target": 0.0,
}


@dataclass
class RequestCtx:
    spec: Spec
    state: StateStore
    op: Operation
    path_params: dict[str, Any]
    query: dict[str, str]
    body: Any
    mission_duration: float = MISSION_DURATION_S
    # Bound by app.Emulator: seed_collection(key, collection_path) populates a
    # generic collection exactly as a GET on it would, so overrides can check
    # referential integrity against not-yet-touched collections.
    seed_collection: Callable[[str, str], None] | None = None
    # The validated X-AMR-Session id ("" for the shared default robot). The
    # fleet emulator forwards it on embedded robot calls so session isolation
    # composes across emulators.
    session_id: str = ""
    # Validated X-AMR-Mission-Duration header (seconds), or None. Only
    # POST /mission_queue consumes it: the new entry freezes this as its own
    # duration, so one robot can carry a mix of long hauls and short hops.
    duration_override: float | None = None


# --- fault injection ---------------------------------------------------------
# Drives the robot into the states integrators must handle. Read-side state
# ids beyond the writable {3, 4, 11}: the official swagger never enumerates
# them; they are pinned by MiR's own ROS message table (mir_msgs/RobotState.msg
# in DFKI-NI/mir_robot, mirrored from real robots: EMERGENCYSTOP=10, ERROR=12)
# and match the open-rmf fleet adapter's constants. Error codes here are
# deliberately in a 10xxx emulator range and every description says
# "(emulated fault)" — they are not official MiR error codes.
FAULTS: dict[str, dict[str, Any]] = {
    "emergency_stop": {
        "description": "Emergency stop pressed: state 10, execution freezes until cleared.",
        "state_id": 10,
        "state_text": "EmergencyStop",
        "holds": True,
        "error": {
            "code": 10010,
            "description": "Emergency stop pressed (emulated fault)",
            "module": "SafetySystem",
            "non_resettable": True,
        },
    },
    "error": {
        "description": "General error: state 12; clears via PUT /status {'clear_error': true}.",
        "state_id": 12,
        "state_text": "Error",
        "holds": True,
        "resettable": True,
        "error": {
            "code": 10012,
            "description": "General error (emulated fault)",
            "module": "MissionController",
            "non_resettable": False,
        },
    },
    "localization_lost": {
        "description": "Robot lost localization: state 12; clear_error resets it.",
        "state_id": 12,
        "state_text": "Error",
        "holds": True,
        "resettable": True,
        "error": {
            "code": 10013,
            "description": "Robot is not localized (emulated fault)",
            "module": "Localization",
            "non_resettable": False,
        },
    },
    # battery_critical and blocked_path model a physical cause (a drained
    # battery, an obstruction): an error reset cannot remove the cause, so
    # clear_error leaves them active and their errors say non_resettable —
    # they clear only via /_emulator/faults (the "cause removed" action).
    "battery_critical": {
        "description": "Battery forced to 1.5%; state unchanged.",
        "battery": 1.5,
        "error": {
            "code": 10014,
            "description": "Battery level critical (emulated fault)",
            "module": "Battery",
            "non_resettable": True,
        },
    },
    "blocked_path": {
        "description": "Path blocked: an active planner error while the robot keeps trying.",
        "error": {
            "code": 10015,
            "description": "Path is blocked (emulated fault)",
            "module": "Planner",
            "non_resettable": True,
        },
    },
    "mission_failure": {
        "description": ("Running and queued missions abort; robot enters Error until clear_error."),
        "state_id": 12,
        "state_text": "Error",
        "resettable": True,
        "aborts_queue": True,
        "error": {
            "code": 10016,
            "description": "Mission failed (emulated fault)",
            "module": "MissionController",
            "non_resettable": False,
        },
    },
    # A rebooting (or network-partitioned) robot doesn't answer with an HTTP
    # status — the connection dies. While active, every API request is
    # severed mid-response (a transport error client-side); the /_emulator/*
    # surfaces stay reachable so the fault can be cleared. Needs a real
    # server (uvicorn): in-process ASGI test clients surface the abort as an
    # exception instead of a closed socket.
    "connection_drop": {
        "description": "Connections sever mid-response, like a rebooting robot; API unreachable.",
        "drops_connections": True,
        "error": {
            "code": 10017,
            "description": "Connection dropped (emulated fault)",
            "module": "Comms",
            "non_resettable": True,
        },
    },
}


def active_faults(state: StateStore) -> list[str]:
    return [n for n in state.singleton("/faults", {"active": []}).get("active", []) if n in FAULTS]


def _sim_clock_for(state: StateStore) -> float:
    """Simulation time computed from raw state (for callers without a ctx)."""
    sim = state.singleton("/mission_sim", {"paused_at": None, "paused_total": 0.0, "hold": None})
    paused = sim.get("paused_total", 0.0)
    if sim.get("paused_at") is not None:
        paused += _now() - sim["paused_at"]
    return _now() - paused


def _abort_queue(state: StateStore, mission_duration: float) -> None:
    """Mark every not-yet-finished queue entry aborted at the current sim
    instant; missions that already ran to completion keep their history."""
    now = _sim_clock_for(state)
    items = sorted(
        state.collection("/mission_queue").items(),
        key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0,
    )
    for entry, _start, finish in _windows(items, mission_duration):
        if finish > now:
            entry.setdefault("_aborted_at", now)


ERROR_REPORT_KEY = "/log/error_reports"


def _log_error_report(state: StateStore, description: str, module: str) -> None:
    """Append a spec-shaped entry to the /log/error_reports collection —
    exactly what a real robot accumulates when a fault fires. Uses the
    generic CRUD storage key, so GET/DELETE on the official endpoint keep
    their semantics over these entries."""
    existing = state.collection(ERROR_REPORT_KEY)
    next_id = max((int(k) for k in existing if k.isdigit()), default=0) + 1
    state.insert(
        ERROR_REPORT_KEY,
        str(next_id),
        {
            "id": next_id,
            "time": _iso(_sim_clock_for(state)),
            "description": description,
            "module": module,
            "generating": False,
            "ready": True,
            "download_url": f"/v2.0.0/log/error_reports/{next_id}/download",
        },
    )


def set_faults(
    state: StateStore, names: list[str], mission_duration: float = MISSION_DURATION_S
) -> None:
    """Replace the active fault set; holding faults freeze the sim clock;
    aborting faults kill the mission queue at the current sim instant.
    Every newly activated fault leaves an error report in the official log."""
    previous = set(active_faults(state))
    state.merge_singleton("/faults", {"active": [n for n in names if n in FAULTS]})
    newly_active = set(active_faults(state)) - previous
    for name in (n for n in names if n in newly_active):
        error = FAULTS[name]["error"]
        _log_error_report(state, error["description"], error["module"])
    if any(FAULTS[n].get("aborts_queue") for n in newly_active):
        _abort_queue(state, mission_duration)
    holds = any(FAULTS[n].get("holds") for n in active_faults(state))
    sim = state.singleton("/mission_sim", {"paused_at": None, "paused_total": 0.0, "hold": None})
    if holds and sim.get("paused_at") is None:
        state.merge_singleton("/mission_sim", {"paused_at": _now(), "hold": "fault"})
    elif not holds and sim.get("hold") == "fault" and sim.get("paused_at") is not None:
        state.merge_singleton(
            "/mission_sim",
            {
                "paused_at": None,
                "paused_total": sim.get("paused_total", 0.0) + (_now() - sim["paused_at"]),
                "hold": None,
            },
        )


def faults_doc(state: StateStore) -> dict:
    return {
        "active": active_faults(state),
        "available": {name: fault["description"] for name, fault in FAULTS.items()},
        "clearing": (
            'PUT {"faults": [...]} replaces the set; DELETE clears everything; '
            'resettable faults also clear via PUT /status {"clear_error": true}'
        ),
    }


# --- mission simulation core -------------------------------------------------


def _sim(ctx: RequestCtx) -> dict:
    return ctx.state.singleton(
        "/mission_sim", {"paused_at": None, "paused_total": 0.0, "hold": None}
    )


def _sim_clock(ctx: RequestCtx) -> float:
    """Simulation time: wall clock minus every paused interval."""
    sim = _sim(ctx)
    paused = sim.get("paused_total", 0.0)
    if sim.get("paused_at") is not None:
        paused += _now() - sim["paused_at"]
    return _now() - paused


def _is_paused(ctx: RequestCtx) -> bool:
    return _sim(ctx).get("paused_at") is not None


def _pause_sim(ctx: RequestCtx, hold: str) -> None:
    """Freeze the sim clock. hold is 'pause' (state 4) or 'manual' (state 11);
    a robot under manual control does not execute missions either."""
    if not _is_paused(ctx):
        ctx.state.merge_singleton("/mission_sim", {"paused_at": _now()})
    ctx.state.merge_singleton("/mission_sim", {"hold": hold})


def _resume_sim(ctx: RequestCtx) -> None:
    sim = _sim(ctx)
    if sim.get("paused_at") is not None:
        ctx.state.merge_singleton(
            "/mission_sim",
            {
                "paused_at": None,
                "paused_total": sim.get("paused_total", 0.0) + (_now() - sim["paused_at"]),
                "hold": None,
            },
        )


def _windows(items: list[tuple[str, dict]], duration: float) -> list[tuple[dict, float, float]]:
    """(entry, start, finish) per queued mission — FIFO, one robot at a time.
    Each entry runs for its own frozen duration (stored at enqueue time, so
    an X-AMR-Mission-Duration override sticks to exactly that entry); the
    parameter is the fallback for entries that predate the field. An aborted
    entry's window collapses at its abort instant (a pending one never runs
    at all), freeing the robot for whatever follows."""
    out: list[tuple[dict, float, float]] = []
    cursor: float | None = None
    for _id, entry in items:
        queued = float(entry.get("_queued_at", 0.0))
        start = queued + MISSION_PENDING_LAG_S
        if cursor is not None:
            start = max(start, cursor)
        finish = start + float(entry.get("_duration_s", duration))
        aborted_at = entry.get("_aborted_at")
        if aborted_at is not None:
            start = min(start, float(aborted_at))
            finish = max(start, float(aborted_at))
        out.append((entry, start, finish))
        cursor = finish
    return out


def _timeline(ctx: RequestCtx) -> list[tuple[dict, float, float]]:
    items = sorted(
        ctx.state.collection("/mission_queue").items(),
        key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0,
    )
    return _windows(items, ctx.mission_duration)


def _entry_state(entry: dict, start: float, finish: float, clock: float) -> str:
    if entry.get("_aborted_at") is not None:
        return "Aborted"
    if clock < start:
        return "Pending"
    if clock < finish:
        return "Executing"
    return "Done"


def _iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts))


def _public_entry(entry: dict, start: float, finish: float, clock: float) -> dict:
    """Queue entry as the API returns it. Per the spec, `ordered`, `started`
    and `finished` are 'the date and time when the mission was queued/started/
    finished' — derived from the timeline; not-yet-reached ones are omitted,
    exactly like a real robot leaves them unset until they happen."""
    public = {k: v for k, v in entry.items() if not k.startswith("_")}
    public["state"] = _entry_state(entry, start, finish, clock)
    public["ordered"] = _iso(float(entry.get("_queued_at", start)))
    public.pop("started", None)
    public.pop("finished", None)
    if clock >= start:
        public["started"] = _iso(start)
    if clock >= finish:
        public["finished"] = _iso(finish)
    if public.get("id") is not None:
        public["url"] = f"/v2.0.0/mission_queue/{public['id']}"
    if isinstance(public.get("mission_id"), str) and public["mission_id"]:
        public["mission"] = f"/v2.0.0/missions/{public['mission_id']}"
    return public


def _executed_seconds_for(state: StateStore, mission_duration: float) -> float:
    """Total mission-executing seconds so far (for callers without a ctx)."""
    clock = _sim_clock_for(state)
    items = sorted(
        state.collection("/mission_queue").items(),
        key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0,
    )
    return sum(
        max(0.0, min(clock, finish) - start)
        for _e, start, finish in _windows(items, mission_duration)
    )


def _executed_seconds(ctx: RequestCtx) -> float:
    return _executed_seconds_for(ctx.state, ctx.mission_duration)


# --- battery model -------------------------------------------------------
# Default: BATTERY_START minus BATTERY_DRAIN_PER_S per executing second.
# /_emulator/battery re-anchors the model (set a level, run a charging
# curve); everything stays derived-at-read-time from the sim clock, so a
# paused or held robot neither drains nor charges and frozen-clock tests
# hold. The battery_critical fault still wins over all of this in /status.

BATTERY_FIELDS = ("percentage", "charging", "charge_rate", "target")
_BATTERY_USAGE = (
    'Body must set one or more of {"percentage": 0-100, "charging": true|false, '
    '"charge_rate": percent per simulated second, "target": 0-100}'
)
_BATTERY_DEFAULTS: dict[str, Any] = {
    "anchor_pct": None,
    "anchor_executed_s": 0.0,
    "charging": False,
    "charge_anchor_clock": None,
    "charge_rate": CHARGE_RATE_DEFAULT,
    "target_pct": CHARGE_TARGET_DEFAULT,
}


def _battery_state(state: StateStore) -> dict:
    return state.singleton("/battery", dict(_BATTERY_DEFAULTS))


def _battery_level(state: StateStore, clock: float, executed_s: float) -> float:
    battery = _battery_state(state)
    anchor = battery.get("anchor_pct")
    base = BATTERY_START if anchor is None else float(anchor)
    anchored_s = float(battery.get("anchor_executed_s", 0.0))
    drained = BATTERY_DRAIN_PER_S * max(0.0, executed_s - anchored_s)
    level = max(min(BATTERY_FLOOR, base), base - drained)
    if battery.get("charging") and battery.get("charge_anchor_clock") is not None:
        rate = float(battery.get("charge_rate", CHARGE_RATE_DEFAULT))
        gain = rate * max(0.0, clock - float(battery["charge_anchor_clock"]))
        # The curve tops out at the target; a level already above it stays
        # put — a charger never discharges the robot.
        cap = max(float(battery.get("target_pct", CHARGE_TARGET_DEFAULT)), base)
        level = min(level + gain, cap)
    return max(0.0, min(100.0, level))


def set_battery(
    state: StateStore, body: Any, mission_duration: float = MISSION_DURATION_S
) -> str | None:
    """Apply a PUT /_emulator/battery body; returns an error string or None.
    Every successful PUT re-anchors the model at the current (or given)
    level, so drain and charge resume from what /status just reported."""
    if not isinstance(body, dict) or not body:
        return _BATTERY_USAGE
    unknown = sorted(set(body) - set(BATTERY_FIELDS))
    if unknown:
        return f"Unknown fields {unknown}; allowed: {sorted(BATTERY_FIELDS)}"

    def _number(value: Any) -> bool:
        return isinstance(value, int | float) and not isinstance(value, bool)

    percentage = body.get("percentage")
    if percentage is not None and not (_number(percentage) and 0 <= percentage <= 100):
        return "percentage must be a number in [0, 100]"
    if "charging" in body and not isinstance(body["charging"], bool):
        return "charging must be true or false"
    rate = body.get("charge_rate")
    if rate is not None and not (_number(rate) and 0 < rate <= 100):
        return "charge_rate must be a number in (0, 100] percent per simulated second"
    target = body.get("target")
    if target is not None and not (_number(target) and 0 <= target <= 100):
        return "target must be a number in [0, 100]"

    clock = _sim_clock_for(state)
    executed = _executed_seconds_for(state, mission_duration)
    current = _battery_state(state)
    level = float(percentage) if percentage is not None else _battery_level(state, clock, executed)
    charging = bool(body.get("charging", current.get("charging", False)))
    state.merge_singleton(
        "/battery",
        {
            "anchor_pct": level,
            "anchor_executed_s": executed,
            "charging": charging,
            "charge_anchor_clock": clock if charging else None,
            "charge_rate": float(
                rate if rate is not None else current.get("charge_rate", CHARGE_RATE_DEFAULT)
            ),
            "target_pct": float(
                target if target is not None else current.get("target_pct", CHARGE_TARGET_DEFAULT)
            ),
        },
    )
    return None


def reset_battery(state: StateStore) -> None:
    """Back to the stock drain-only model, as if the surface was never used."""
    state.merge_singleton("/battery", dict(_BATTERY_DEFAULTS))


def battery_doc(state: StateStore, mission_duration: float = MISSION_DURATION_S) -> dict:
    clock = _sim_clock_for(state)
    level = _battery_level(state, clock, _executed_seconds_for(state, mission_duration))
    for name in active_faults(state):
        if "battery" in FAULTS[name]:
            level = FAULTS[name]["battery"]  # faults win, exactly as /status reports
    battery = _battery_state(state)
    return {
        "percentage": round(level, 2),
        "charging": bool(battery.get("charging", False)),
        "charge_rate": float(battery.get("charge_rate", CHARGE_RATE_DEFAULT)),
        "target": float(battery.get("target_pct", CHARGE_TARGET_DEFAULT)),
        "drain_per_s": BATTERY_DRAIN_PER_S,
        "usage": _BATTERY_USAGE,
    }


# --- time scaling --------------------------------------------------------------
# Speeding up a test by shortening durations (--mission-duration 3, hot
# charge_rate) makes the emitted timestamps lie: a "two minute" mission shows
# a three-second window. Scaling the clock instead keeps every simulated
# duration — mission windows, battery curves, `ordered/started/finished` —
# realistic while the wall wait shrinks. Process-wide (one clock, every
# session and embedded fleet robot); anchored at the current simulated
# instant on every change, because rewinding would flip Done missions back
# to Executing.
TIME_SCALE_MIN = 0.001  # slow motion is allowed; zero and negatives are not
TIME_SCALE_MAX = 3600.0  # an hour of simulation per wall second is plenty
_TIME_SCALE_USAGE = (
    f'Body must be {{"scale": <simulated seconds per wall second, '
    f"{TIME_SCALE_MIN}-{TIME_SCALE_MAX}>}}"
)
_time_scale: float = 1.0


def set_time_scale(body: Any) -> str | None:
    """Apply a PUT /_emulator/clock body; returns an error string or None."""
    if not isinstance(body, dict):
        return _TIME_SCALE_USAGE
    scale = body.get("scale")
    if isinstance(scale, bool) or not isinstance(scale, int | float):
        return _TIME_SCALE_USAGE
    if not math.isfinite(scale) or not (TIME_SCALE_MIN <= scale <= TIME_SCALE_MAX):
        return _TIME_SCALE_USAGE

    global _now, _time_scale
    anchor_sim = _now()
    anchor_wall = _wall_clock()

    def scaled_clock() -> float:
        return anchor_sim + (_wall_clock() - anchor_wall) * scale

    _now = scaled_clock
    _time_scale = float(scale)
    return None


def reset_time_scale() -> None:
    """Back to real time (scale 1.0). Simulated time keeps whatever offset it
    accumulated — continuity over wall-clock agreement."""
    set_time_scale({"scale": 1.0})


def clock_doc() -> dict:
    return {
        "scale": _time_scale,
        "sim_time": _iso(_now()),
        "wall_time": _iso(_wall_clock()),
        "usage": (
            'PUT {"scale": N} runs simulated time at N seconds per wall second, '
            "process-wide (all sessions, all embedded robots); DELETE restores "
            "1.0. Changing scale never rewinds simulated time."
        ),
    }


def _declared_only(ctx: RequestCtx, doc: dict) -> dict:
    """*doc* restricted to the fields the op's success schema declares.

    The official files answer some operations with slimmer documents than the
    emulator's internal entries carry (POST /mission_queue and the GET list
    return GetMission_queues {id, state, url}; GET /registers/{id} returns
    GetRegister without the list shape's url) — never emit more than the spec
    states. A schema without declared properties leaves *doc* untouched."""
    schema = ctx.spec.deref(ctx.op.success_schema)
    if schema.get("type") == "array":
        schema = schema.get("items") or {}
    props = schema.get("properties")
    if not isinstance(props, dict) or not props:
        return doc
    return {key: value for key, value in doc.items() if key in props}


def _mission_waypoints(ctx: RequestCtx, mission_id: Any) -> list[dict]:
    """The mission's move-action waypoints, in priority order.

    Real MiR missions are lists of actions; a move action's parameters
    carry {"id": "position", "value": <position-guid>}. Actions live in the
    generic /missions/{mission_id}/actions collection, positions in
    /positions — only references that resolve to a stored position with
    coordinates count (seeded placeholders don't)."""
    if not mission_id:
        return []
    actions = ctx.state.collection(f"/missions/{{mission_id}}/actions?mission_id={mission_id}")
    positions: dict[str, dict] = {}
    for stored in ctx.state.collection("/positions").values():
        if not stored.get("guid"):
            continue
        # coordinates live on the client's stored request (the list schema
        # carries only guid/map/name/type_id)
        request = stored.get("_request")
        if not isinstance(request, dict):
            request = {}
        positions[str(stored["guid"])] = {**stored, **request}
    waypoints: list[dict] = []
    for action in sorted(actions.values(), key=lambda a: float(a.get("priority") or 0)):
        # the response schema types parameters as a string (a real MiR spec
        # quirk), so the client's actual array lives on the stored request
        request = action.get("_request")
        if not isinstance(request, dict):
            request = {}
        parameters = request.get("parameters")
        if not isinstance(parameters, list):
            parameters = action.get("parameters")
        for parameter in parameters if isinstance(parameters, list) else []:
            if not (isinstance(parameter, dict) and parameter.get("id") == "position"):
                continue
            target = positions.get(str(parameter.get("value")))
            if isinstance(target, dict) and "pos_x" in target and "pos_y" in target:
                waypoints.append(target)
    return waypoints


def _along_polyline(
    points: list[tuple[float, float]], fraction: float
) -> tuple[float, float, float]:
    """(x, y, heading°) at *fraction* of the polyline's total length."""
    lengths = [math.dist(p0, p1) for p0, p1 in itertools.pairwise(points)]
    total = sum(lengths)
    if total <= 0:
        x, y = points[-1]
        return x, y, 0.0
    target = max(0.0, min(1.0, fraction)) * total
    covered = 0.0
    for (p0, p1), segment in zip(itertools.pairwise(points), lengths, strict=True):
        (x0, y0), (x1, y1) = p0, p1
        if segment and target <= covered + segment:
            t = (target - covered) / segment
            heading = math.degrees(math.atan2(y1 - y0, x1 - x0))
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, heading
        covered += segment
    x, y = points[-1]
    return x, y, 0.0


def _waypoint_pose(
    ctx: RequestCtx, timeline: list[tuple[dict, float, float]], clock: float
) -> dict | None:
    """Pose from mission waypoints, or None when the patrol model applies.

    Executing a waypoint mission interpolates along anchor → waypoints,
    where the anchor is the last finished waypoint mission's final waypoint
    (consecutive missions chain) or the relocalized/home position. Idle
    after a waypoint mission rests at its final waypoint."""
    overlay = ctx.state.singleton("/status", {})
    user_pos = overlay.get("position")
    if not isinstance(user_pos, dict):
        user_pos = {}
    anchor = (
        float(user_pos.get("x", POSITION_HOME_X)),
        float(user_pos.get("y", POSITION_HOME_Y)),
    )
    rest: dict | None = None
    for entry, start, finish in timeline:
        if finish <= clock:
            waypoints = _mission_waypoints(ctx, entry.get("mission_id"))
            if waypoints:
                rest = waypoints[-1]
        elif start <= clock:  # and clock < finish, given the branch above
            waypoints = _mission_waypoints(ctx, entry.get("mission_id"))
            if not waypoints:
                return None  # executing a plain mission: patrol model
            if rest is not None:
                anchor = (float(rest["pos_x"]), float(rest["pos_y"]))
            points = [anchor] + [(float(w["pos_x"]), float(w["pos_y"])) for w in waypoints]
            fraction = (clock - start) / (finish - start) if finish > start else 1.0
            x, y, heading = _along_polyline(points, fraction)
            return {"x": round(x, 2), "y": round(y, 2), "orientation": round(heading, 1)}
    if rest is not None:
        return {
            "x": round(float(rest["pos_x"]), 2),
            "y": round(float(rest["pos_y"]), 2),
            "orientation": float(rest.get("orientation", 0.0)),
        }
    return None


def _mission_snapshot(ctx: RequestCtx) -> dict:
    """Sim-derived /status fields: state, battery, odometry, position."""
    clock = _sim_clock(ctx)
    timeline = _timeline(ctx)
    executed_s = _executed_seconds(ctx)
    battery = _battery_level(ctx.state, clock, executed_s)
    distance = MISSION_SPEED_M_S * executed_s
    paused = _is_paused(ctx)

    fields: dict[str, Any] = {
        "battery_percentage": round(battery, 2),
        "battery_time_remaining": int(battery * BATTERY_SECONDS_PER_PERCENT),
        "moved": round(1204.5 + distance, 2),
        "_distance_m": distance,
        "_waypoint_pose": _waypoint_pose(ctx, timeline, clock),
    }

    hold_id = 11 if _sim(ctx).get("hold") == "manual" else 4
    executing = next(((e, s, f) for e, s, f in timeline if s <= clock < f), None)
    if executing is not None:
        entry, _start, finish = executing
        remaining = finish - clock
        fields.update(
            {
                "state_id": hold_id if paused else 5,
                "state_text": STATE_CHOICES[hold_id] if paused else "Executing",
                "mission_queue_id": int(entry.get("id", 0)),
                "mission_queue_url": f"/v2.0.0/mission_queue/{entry.get('id')}",
                "mission_text": f"Executing mission (queue id {entry.get('id')})...",
                "distance_to_next_target": round(remaining * MISSION_SPEED_M_S, 2),
            }
        )
    elif paused:
        fields.update({"state_id": hold_id, "state_text": STATE_CHOICES[hold_id]})
    return fields


def _status_doc(ctx: RequestCtx) -> dict:
    """Layering, later wins: schema example → STATUS_OVERLAY → user PUTs →
    simulation. The sim owns robot state / battery / odometry while missions
    run; user-set fields like robot_name always survive."""
    op = ctx.spec.operations.get(("GET", "/status"), ctx.op)
    base = example_from_schema(ctx.spec.deref(op.success_schema))
    if isinstance(base, dict):
        overlay_compatible(base, STATUS_OVERLAY)
    doc = dict(base) if isinstance(base, dict) else {}
    overlay = ctx.state.singleton("/status", {})
    for key, value in overlay.items():
        if key in doc:
            doc[key] = value

    snapshot = _mission_snapshot(ctx)
    distance = snapshot.pop("_distance_m")
    waypoint_pose = snapshot.pop("_waypoint_pose")
    for key, value in snapshot.items():
        if key in doc:
            doc[key] = value
    if "uptime" in doc:
        clock = _sim_clock(ctx)
        boot = ctx.state.singleton("/boot", {"at": clock - UPTIME_START_S})
        doc["uptime"] = int(clock - boot["at"])
    if isinstance(doc.get("position"), dict) and waypoint_pose is not None:
        # Mission move-actions define the path: the pose rides the waypoint
        # polyline (or rests at the last mission's final waypoint).
        position = dict(doc["position"])
        position.update(waypoint_pose)
        doc["position"] = position
    elif isinstance(doc.get("position"), dict):
        position = dict(doc["position"])
        # Patrol a straight out-and-back segment of the loop. A position set
        # via PUT /status relocalizes the robot: it becomes the loop's home
        # and the patrol offset restarts from the odometry at that moment.
        user_pos = overlay.get("position")
        if not isinstance(user_pos, dict):
            user_pos = {}
        home_x = float(user_pos.get("x", POSITION_HOME_X))
        home_y = float(user_pos.get("y", POSITION_HOME_Y))
        along_loop = (distance - float(overlay.get("_position_anchor_m", 0.0))) % LOOP_LENGTH_M
        half = LOOP_LENGTH_M / 2
        offset = along_loop if along_loop <= half else LOOP_LENGTH_M - along_loop
        orientation = 0.0 if along_loop <= half else 180.0
        if along_loop == 0.0 and "orientation" in user_pos:
            orientation = float(user_pos["orientation"])
        position.update({"x": round(home_x + offset, 2), "y": home_y, "orientation": orientation})
        doc["position"] = position
    if isinstance(doc.get("velocity"), dict):
        moving = snapshot.get("state_text") == "Executing"
        velocity = dict(doc["velocity"])
        if "linear" in velocity:
            velocity["linear"] = MISSION_SPEED_M_S if moving else 0.0
        if "angular" in velocity:
            velocity["angular"] = 0.0
        doc["velocity"] = velocity

    # Injected faults are the outermost layer: they win over user PUTs and
    # the simulation, exactly like a physical fault would.
    active = active_faults(ctx.state)
    if active:
        if "errors" in doc:
            doc["errors"] = [dict(FAULTS[name]["error"]) for name in active]
        for name in active:
            fault = FAULTS[name]
            if "battery" in fault:
                if "battery_percentage" in doc:
                    doc["battery_percentage"] = fault["battery"]
                if "battery_time_remaining" in doc:
                    doc["battery_time_remaining"] = int(
                        fault["battery"] * BATTERY_SECONDS_PER_PERCENT
                    )
        state_fault = next((FAULTS[n] for n in active if "state_id" in FAULTS[n]), None)
        if state_fault is not None:
            if "state_id" in doc:
                doc["state_id"] = state_fault["state_id"]
            if "state_text" in doc:
                doc["state_text"] = state_fault["state_text"]
            if "velocity" in doc and isinstance(doc["velocity"], dict):
                doc["velocity"] = {k: 0.0 for k in doc["velocity"]}
    return doc


async def get_status(ctx: RequestCtx) -> tuple[int, Any]:
    return ctx.op.success_status, _status_doc(ctx)


def _argument_error(human: str) -> tuple[int, Any]:
    return 400, {"error_code": "400", "error_human": f"Argument error: {human}"}


async def put_status(ctx: RequestCtx) -> tuple[int, Any]:
    """Apply exactly the fields the spec's PutStatus document declares — a
    real robot ignores everything else. MiR semantics per the spec: state_id
    4 pauses the robot, 11 puts it in manual control, 3 sets it Ready again;
    pausing (or taking manual control) freezes the simulation clock, so a
    held mission keeps its progress and resumes exactly where it stopped.
    `name` renames the robot; `position` relocalizes it (see _status_doc)."""
    body = ctx.body if isinstance(ctx.body, dict) else {}

    state_id = body.get("state_id")
    if state_id is not None and state_id not in STATE_CHOICES:
        return _argument_error(f"state_id choices are {sorted(STATE_CHOICES)}")
    mode_id = body.get("mode_id")
    if mode_id is not None and mode_id not in MODE_CHOICES:
        return _argument_error(f"mode_id choices are {sorted(MODE_CHOICES)}")
    if "clear_error" in body and body["clear_error"] is not True:
        return _argument_error("clear_error choices are {True}")

    if state_id == 4:
        _pause_sim(ctx, "pause")
    elif state_id == 11:
        _pause_sim(ctx, "manual")
    elif state_id == 3:
        _resume_sim(ctx)

    patch: dict[str, Any] = {}
    for put_field, status_field in (
        ("name", "robot_name"),
        ("serial_number", "serial_number"),
        ("map_id", "map_id"),
    ):
        if isinstance(body.get(put_field), str):
            patch[status_field] = body[put_field]
    if mode_id is not None:
        patch["mode_id"] = mode_id
        patch["mode_text"] = MODE_CHOICES[mode_id]
    if isinstance(body.get("position"), dict):
        position = {
            k: float(v)
            for k, v in body["position"].items()
            if k in ("x", "y", "orientation")
            and isinstance(v, int | float)
            and not isinstance(v, bool)
        }
        if position:
            patch["position"] = position
            patch["_position_anchor_m"] = _executed_seconds(ctx) * MISSION_SPEED_M_S
    if body.get("clear_error") is True:
        patch["errors"] = []
        # A real robot's error reset clears resettable faults; an emergency
        # stop cannot be cleared from the API.
        remaining = [n for n in active_faults(ctx.state) if not FAULTS[n].get("resettable")]
        set_faults(ctx.state, remaining, ctx.mission_duration)
    if patch:
        ctx.state.merge_singleton("/status", patch)
    return ctx.op.success_status, _status_doc(ctx)


def _mission_exists(ctx: RequestCtx, mission_id: Any) -> bool:
    """True when mission_id names a mission on this robot (seeded or created)."""
    if not isinstance(mission_id, str) or not mission_id:
        return False
    if ctx.seed_collection is not None:
        ctx.seed_collection("/missions", "/missions")
    missions = ctx.state.collection("/missions")
    return mission_id in missions or any(
        item.get("guid") == mission_id for item in missions.values()
    )


async def post_mission_queue(ctx: RequestCtx) -> tuple[int, Any]:
    # A real robot rejects queueing a mission it does not know (400 is the
    # declared "Bad request or Argument error" response for this operation).
    mission_id = ctx.body.get("mission_id") if isinstance(ctx.body, dict) else None
    if not _mission_exists(ctx, mission_id):
        return _argument_error("mission_id does not match an existing mission")
    entry = example_from_schema(ctx.spec.deref(ctx.op.success_schema))
    if not isinstance(entry, dict):
        entry = {}
    if isinstance(ctx.body, dict):
        entry.update(ctx.body)
    queue_id = ctx.state.next_int_id()
    entry["id"] = queue_id
    entry["_queued_at"] = _sim_clock(ctx)
    entry["_duration_s"] = (
        ctx.duration_override if ctx.duration_override is not None else ctx.mission_duration
    )
    ctx.state.insert("/mission_queue", str(queue_id), entry)
    ctx.state.merge_singleton("/status", {"mission_queue_id": queue_id})
    clock = _sim_clock(ctx)
    for stored, start, finish in _timeline(ctx):
        if stored is entry:
            return ctx.op.success_status, _declared_only(
                ctx, _public_entry(stored, start, finish, clock)
            )
    return ctx.op.success_status, _declared_only(
        ctx, _public_entry(entry, clock + 1, clock + 2, clock)
    )


async def get_mission_queue(ctx: RequestCtx) -> tuple[int, Any]:
    clock = _sim_clock(ctx)
    return ctx.op.success_status, [
        _declared_only(ctx, _public_entry(entry, start, finish, clock))
        for entry, start, finish in _timeline(ctx)
    ]


async def get_mission_queue_item(ctx: RequestCtx) -> tuple[int, Any]:
    try:
        queue_id = int(next(iter(ctx.path_params.values())))
    except (StopIteration, TypeError, ValueError):
        return 404, {"error_code": "404", "error_human": "Not found"}
    clock = _sim_clock(ctx)
    for entry, start, finish in _timeline(ctx):
        if entry.get("id") != queue_id:
            continue
        public = _public_entry(entry, start, finish, clock)
        # The item endpoint returns the full GetMission_queue document (the
        # list uses the slim {id, state, url} shape) — flesh it out from the
        # declared schema, then overlay the live lifecycle fields.
        full = example_from_schema(ctx.spec.deref(ctx.op.success_schema))
        if not isinstance(full, dict) or not full:
            return ctx.op.success_status, _declared_only(ctx, public)
        overlay_compatible(full, public)
        for key in ("started", "finished"):
            if key in public:
                full[key] = public[key]
            else:
                full.pop(key, None)
        return ctx.op.success_status, full
    return 404, {"error_code": "404", "error_human": "Not found"}


async def put_mission_queue_item(ctx: RequestCtx) -> tuple[int, Any]:
    """PutMission_queue declares cmd, mission_id, priority. Metadata updates
    apply to the stored entry; the generic handler would instead seed a
    phantom entry into a queue that never held one."""
    try:
        queue_id = int(next(iter(ctx.path_params.values())))
    except (StopIteration, TypeError, ValueError):
        return 404, {"error_code": "404", "error_human": "Not found"}
    if ctx.state.get("/mission_queue", str(queue_id)) is None:
        return 404, {"error_code": "404", "error_human": "Not found"}
    body = ctx.body if isinstance(ctx.body, dict) else {}
    patch = {k: body[k] for k in ("mission_id", "priority") if k in body}
    if "mission_id" in patch and not _mission_exists(ctx, patch["mission_id"]):
        return _argument_error("mission_id does not match an existing mission")
    if patch:
        ctx.state.update("/mission_queue", str(queue_id), patch)
    return await get_mission_queue_item(ctx)


async def delete_mission_queue(ctx: RequestCtx) -> tuple[int, Any]:
    ctx.state.clear("/mission_queue")
    ctx.state.merge_singleton("/status", {"mission_queue_id": 0, "mission_text": ""})
    return ctx.op.success_status, None


async def delete_mission_queue_item(ctx: RequestCtx) -> tuple[int, Any]:
    """Remove one queue entry — never executes (if pending) or stops on the
    spot (if executing); the FIFO timeline recomputes without it. The generic
    handler would seed an example entry first, which a real queue never has."""
    try:
        queue_id = int(next(iter(ctx.path_params.values())))
    except (StopIteration, TypeError, ValueError):
        return 404, {"error_code": "404", "error_human": "Not found"}
    if not ctx.state.delete("/mission_queue", str(queue_id)):
        return 404, {"error_code": "404", "error_human": "Not found"}
    return ctx.op.success_status, None if ctx.op.success_status == 204 else {}


def _register_doc(ctx: RequestCtx, register_id: int) -> dict:
    register = ctx.state.singleton("/registers", {}).get(str(register_id), {})
    return {
        "id": register_id,
        "label": str(register.get("label", "")),
        "url": f"/v2.0.0/registers/{register_id}",
        "value": float(register.get("value", 0.0)),
    }


async def get_registers(ctx: RequestCtx) -> tuple[int, Any]:
    return ctx.op.success_status, [
        _declared_only(ctx, _register_doc(ctx, i)) for i in range(1, REGISTER_COUNT + 1)
    ]


def _register_id(ctx: RequestCtx) -> int | None:
    try:
        register_id = int(next(iter(ctx.path_params.values())))
    except (StopIteration, TypeError, ValueError):
        return None
    return register_id if 1 <= register_id <= REGISTER_COUNT else None


async def get_register(ctx: RequestCtx) -> tuple[int, Any]:
    register_id = _register_id(ctx)
    if register_id is None:
        return 404, {"error_code": "404", "error_human": "register not found"}
    return ctx.op.success_status, _declared_only(ctx, _register_doc(ctx, register_id))


async def put_register(ctx: RequestCtx) -> tuple[int, Any]:
    """PUT and POST /registers/{id}: the spec's PostRegister body is
    {value: number, label: string}, both optional — writes merge."""
    register_id = _register_id(ctx)
    if register_id is None:
        return 404, {"error_code": "404", "error_human": "register not found"}
    body = ctx.body if isinstance(ctx.body, dict) else {}
    patch: dict[str, Any] = {}
    if "value" in body:
        if not isinstance(body["value"], int | float) or isinstance(body["value"], bool):
            return _argument_error("value must be a number")
        patch["value"] = float(body["value"])
    if "label" in body:
        if not isinstance(body["label"], str):
            return _argument_error("label must be a string")
        patch["label"] = body["label"]
    if patch:
        current = ctx.state.singleton("/registers", {}).get(str(register_id), {})
        ctx.state.merge_singleton("/registers", {str(register_id): {**current, **patch}})
    return ctx.op.success_status, _declared_only(ctx, _register_doc(ctx, register_id))


async def get_metrics(ctx: RequestCtx) -> tuple[int, Any, str]:
    snapshot = _mission_snapshot(ctx)
    clock = _sim_clock(ctx)
    boot = ctx.state.singleton("/boot", {"at": clock - UPTIME_START_S})
    timeline = _timeline(ctx)
    completed = sum(
        1 for entry, _s, finish in timeline if entry.get("_aborted_at") is None and clock >= finish
    )
    aborted = sum(1 for entry, _s, _f in timeline if entry.get("_aborted_at") is not None)
    text = (
        "# TYPE mir_robot_battery_percent gauge\n"
        f"mir_robot_battery_percent {snapshot['battery_percentage']}\n"
        "# TYPE mir_robot_uptime_seconds counter\n"
        f"mir_robot_uptime_seconds_total {int(clock - boot['at'])}\n"
        "# TYPE mir_robot_distance_moved_meters counter\n"
        f"mir_robot_distance_moved_meters_total {snapshot['moved']}\n"
        "# TYPE mir_robot_missions_completed counter\n"
        f"mir_robot_missions_completed_total {completed}\n"
        "# TYPE mir_robot_missions_aborted counter\n"
        f"mir_robot_missions_aborted_total {aborted}\n"
        "# EOF\n"
    )
    return ctx.op.success_status, text, "text/plain; version=0.0.4"


async def get_statistics_distance(ctx: RequestCtx) -> tuple[int, Any]:
    """Per-day driven distance, derived from the mission timeline: executed
    seconds bucketed by sim day x the simulated travel speed. The current
    day is always present (a dashboard's "today" starts at 0), and a mission
    spanning midnight splits between both days — real robots report daily
    statistics, not per-mission ones."""
    clock = _sim_clock(ctx)
    day_s = 86400.0

    def day_of(ts: float) -> float:
        return ts - (ts % day_s)

    buckets: dict[float, float] = {day_of(clock): 0.0}
    for _entry, start, finish in _timeline(ctx):
        end = min(finish, clock)
        cursor = start
        while cursor < end:
            day_end = day_of(cursor) + day_s
            span_end = min(end, day_end)
            buckets[day_of(cursor)] = buckets.get(day_of(cursor), 0.0) + (span_end - cursor)
            cursor = span_end
    return ctx.op.success_status, [
        {"date": _iso(day), "distance": round(seconds * MISSION_SPEED_M_S, 2)}
        for day, seconds in sorted(buckets.items())
    ]


OVERRIDES: dict[tuple[str, str], Any] = {
    ("GET", "/status"): get_status,
    ("PUT", "/status"): put_status,
    ("POST", "/mission_queue"): post_mission_queue,
    ("GET", "/mission_queue"): get_mission_queue,
    ("GET", "/mission_queue/{id}"): get_mission_queue_item,
    ("PUT", "/mission_queue/{id}"): put_mission_queue_item,
    ("DELETE", "/mission_queue"): delete_mission_queue,
    ("DELETE", "/mission_queue/{id}"): delete_mission_queue_item,
    ("GET", "/registers"): get_registers,
    ("GET", "/registers/{id}"): get_register,
    ("PUT", "/registers/{id}"): put_register,
    ("POST", "/registers/{id}"): put_register,
    ("GET", "/metrics"): get_metrics,
    ("GET", "/statistics/distance"): get_statistics_distance,
}
