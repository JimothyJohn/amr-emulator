"""MCP server: natural-language control of MiR robots and fleets.

Every tool wraps the documented MiR REST API (robot ``/api/v2.0.0``, fleet
``/api/v1``) plus the emulator-only test surfaces under ``/_emulator/*``.
Tool results are JSON strings; errors are ``"Error: ..."`` strings with the
fix spelled out, so the calling agent can recover without guessing.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Literal

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from mir_mcp import client

mcp = MCPServer("mir_mcp")

STATE_IDS = {"ready": 3, "pause": 4, "manual_control": 11}

STATUS_FIELDS = (
    "robot_name",
    "state_id",
    "state_text",
    "battery_percentage",
    "battery_time_remaining",
    "position",
    "velocity",
    "mission_text",
    "mission_queue_id",
    "errors",
    "uptime",
)


def _dump(payload: Any) -> str:
    return json.dumps(payload, indent=1, sort_keys=True)


def _as_list(value: Any) -> list:
    """MiR specs declare some list endpoints with the element's object schema,
    and servers differ on which shape they answer with — accept both (same
    defense as mir_client.report._as_list)."""
    if isinstance(value, list):
        return value
    return [value] if isinstance(value, dict) else []


def _trim_status(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: doc[k] for k in STATUS_FIELDS if k in doc}


async def _robot(method: str, path: str, *, json_body: Any = None, api: bool = True) -> str | Any:
    """Run one robot call; return the body, or an 'Error: ...' string."""
    try:
        status, body = await client.robot_request(method, path, json=json_body, api=api)
    except client.TargetResolutionError as exc:
        return str(exc)
    except httpx.HTTPError as exc:
        return client.describe_connection_error(exc, client.robot_base_url())
    if status >= 400:
        return client.describe_http_error(status, body, "robot")
    return body


async def _fleet(method: str, path: str, *, json_body: Any = None) -> str | Any:
    try:
        status, body = await client.fleet_request(method, path, json=json_body)
    except client.TargetResolutionError as exc:
        return str(exc)
    except httpx.HTTPError as exc:
        return client.describe_connection_error(exc, client.fleet_base_url())
    if status >= 400:
        return client.describe_http_error(status, body, "fleet")
    return body


async def _resolve_mission(name_or_guid: str) -> str | dict[str, Any]:
    """Match a user-facing mission name (case-insensitive) or exact guid."""
    missions = await _robot("GET", "/missions")
    if isinstance(missions, str):
        return missions
    entries = _as_list(missions)
    exact = [m for m in entries if m.get("guid") == name_or_guid]
    named = [m for m in entries if str(m.get("name", "")).lower() == name_or_guid.lower()]
    matches = exact or named
    if len(matches) == 1:
        return matches[0]
    available = ", ".join(f"{m.get('name')} ({m.get('guid')})" for m in entries) or "none"
    if not matches:
        return f"Error: no mission named or with guid '{name_or_guid}'. Available: {available}"
    return f"Error: '{name_or_guid}' is ambiguous. Matches: {available}"


async def _target_summary(base: str, resolver) -> dict[str, Any]:
    info = await client.detect_target(base)
    summary: dict[str, Any] = {"url": base, "kind": info["kind"]}
    if info.get("version"):
        summary["software_version"] = info["version"]
    elif info["kind"] == "robot":
        summary["software_version"] = "unknown (target does not publish one)"
    if info["kind"] == "dispatcher":
        summary["available_versions"] = info["versions"]
        summary["available_fleet_versions"] = info["fleet_versions"]
    if info["kind"] == "unknown":
        summary["note"] = (
            "nothing MiR-shaped answered; check the URL or start an emulator "
            "with `uv run mir-emulator`"
        )
        return summary
    try:
        summary["resolved_base"] = await resolver()
    except client.TargetResolutionError as exc:
        summary["error"] = str(exc)
    return summary


@mcp.tool(
    annotations=ToolAnnotations(
        title="Identify the connected MiR target",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_server_info() -> str:
    """Identify what the configured endpoints actually are and which MiR
    software version they run — call this first on a new connection.

    Probes MIR_ROBOT_URL and MIR_FLEET_URL without credentials or state
    changes and reports, per target: kind (robot, fleet, or multi-version
    dispatcher), the detected software version, the resolved API base the
    other tools will use, and — for a dispatcher — every served version
    (pin one with MIR_VERSION / MIR_FLEET_VERSION). No version needs to be
    configured up front; the tools adapt to whatever the target reports.
    """
    doc: dict[str, Any] = {
        "robot_target": await _target_summary(client.robot_base_url(), client.resolved_robot_base)
    }
    # A separate fleet URL always gets its own summary; with a shared URL,
    # only add one when the target actually has a fleet face.
    if client.fleet_base_url() != client.robot_base_url() or doc["robot_target"]["kind"] in (
        "fleet",
        "dispatcher",
    ):
        doc["fleet_target"] = await _target_summary(
            client.fleet_base_url(), client.resolved_fleet_base
        )
    return _dump(doc)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Discover MiR robots on the network",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_discover_robots(hosts: list[str] | None = None) -> str:
    """Find MiR robots, fleets, and emulators on the network by IP — use
    this when you don't know a robot's address.

    Sweeps candidate hosts on the ports MiR gear listens on (80 on real
    robots, 8080 on the emulator), TCP-probes each, and runs the version
    handshake on anything that answers — returning only confirmed MiR
    targets (kind + software version + URL). *hosts* accepts IPs,
    hostnames, and CIDR blocks (e.g. ["192.168.12.0/24"]); omit it to scan
    this machine's local /24. All probes are unauthenticated reads. To then
    control a found target, set MIR_ROBOT_URL / MIR_FLEET_URL to its URL.
    """
    try:
        found = await client.scan_for_targets(hosts)
    except ValueError as exc:
        return f"Error: {exc}"
    except OSError as exc:
        return f"Error: network scan failed ({type(exc).__name__}: {exc})."
    if not found:
        where = ", ".join(hosts) if hosts else "the local /24"
        return _dump(
            {
                "found": [],
                "scanned": where,
                "hint": (
                    "No MiR robots or fleets answered. Check you are on the robot's "
                    "network, or start an emulator with `uv run mir-emulator`."
                ),
            }
        )
    return _dump({"found": found, "count": len(found)})


# ---------------------------------------------------------------- robot tools


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get robot status",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_robot_status() -> str:
    """Read the robot's live status: state, battery, position, current
    mission, and any errors.

    Returns a JSON object with robot_name, state_id/state_text (3 Ready,
    4 Pause, 5 Executing, 10 Emergency stop, 11 Manual control, 12 Error),
    battery_percentage, position {x, y, orientation}, mission_text,
    mission_queue_id and errors[]. Call this first to verify connectivity,
    and after any state change to confirm it took effect.
    """
    body = await _robot("GET", "/status")
    return body if isinstance(body, str) else _dump(_trim_status(body))


@mcp.tool(
    annotations=ToolAnnotations(
        title="Set robot state (ready / pause / manual)",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_set_robot_state(state: Literal["ready", "pause", "manual_control"]) -> str:
    """Pause the robot, resume it, or hand it to manual control.

    'pause' freezes mission execution in place; 'ready' resumes exactly
    where it stopped; 'manual_control' releases the drive to a human with
    the joystick. Maps to the documented PUT /status state_id (3/4/11).
    Returns the resulting status so the caller sees the observed state.
    """
    body = await _robot("PUT", "/status", json_body={"state_id": STATE_IDS[state]})
    return body if isinstance(body, str) else _dump(_trim_status(body))


@mcp.tool(
    annotations=ToolAnnotations(
        title="Clear robot error state",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_clear_error() -> str:
    """Acknowledge and clear the robot's error state (PUT /status
    {"clear_error": true}), the documented recovery for resettable errors.

    An emergency stop cannot be cleared this way — on a real robot the
    physical button must be released; on the emulator use mir_manage_faults.
    Returns the resulting status.
    """
    body = await _robot("PUT", "/status", json_body={"clear_error": True})
    return body if isinstance(body, str) else _dump(_trim_status(body))


@mcp.tool(
    annotations=ToolAnnotations(
        title="List mission definitions",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_list_missions() -> str:
    """List the missions defined on the robot as [{guid, name}, ...].

    Mission guids come from here — never guess one. Use the guid (or the
    unique name) with mir_queue_mission.
    """
    body = await _robot("GET", "/missions")
    if isinstance(body, str):
        return body
    entries = _as_list(body)
    return _dump([{"guid": m.get("guid"), "name": m.get("name")} for m in entries])


@mcp.tool(
    annotations=ToolAnnotations(
        title="Queue a mission",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=True,
    )
)
async def mir_queue_mission(mission: str, wait_seconds: int = 0) -> str:
    """Queue a mission for execution, by name (case-insensitive) or guid.

    The robot works the queue in order: Pending -> Executing -> Done. With
    wait_seconds > 0, polls the queue entry and returns once it reaches
    Done/Aborted or the wait expires (whichever comes first) — the returned
    'state' is always the last observed one. Against a real robot this
    physically moves the vehicle.
    """
    resolved = await _resolve_mission(mission)
    if isinstance(resolved, str):
        return resolved
    entry = await _robot("POST", "/mission_queue", json_body={"mission_id": resolved["guid"]})
    if isinstance(entry, str):
        return entry
    deadline = asyncio.get_event_loop().time() + min(wait_seconds, 300)
    while wait_seconds and entry.get("state") not in ("Done", "Aborted"):
        if asyncio.get_event_loop().time() >= deadline:
            break
        await asyncio.sleep(0.5)
        polled = await _robot("GET", f"/mission_queue/{entry.get('id')}")
        if isinstance(polled, str):
            return polled
        entry = polled
    return _dump({"mission": resolved["name"], "queue_entry": entry})


@mcp.tool(
    annotations=ToolAnnotations(
        title="Show the mission queue",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_mission_queue(queue_id: int | None = None) -> str:
    """Read the mission queue (all entries) or one entry by its integer id.

    Each entry carries id, state (Pending/Executing/Done/Aborted) and
    timestamps. Poll a specific id to watch a queued mission finish.
    """
    path = f"/mission_queue/{queue_id}" if queue_id is not None else "/mission_queue"
    body = await _robot("GET", path)
    return body if isinstance(body, str) else _dump(body)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Cancel queued missions",
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_cancel_missions(queue_id: int | None = None) -> str:
    """Cancel one queued mission by id, or the entire queue when no id is
    given. Destructive: a cleared queue cannot be restored — re-queue the
    missions if needed. On a real robot this stops planned work; confirm
    intent before calling without an id.
    """
    path = f"/mission_queue/{queue_id}" if queue_id is not None else "/mission_queue"
    body = await _robot("DELETE", path)
    # A successful DELETE has an empty body, so only error strings pass through.
    if isinstance(body, str) and body.startswith("Error:"):
        return body
    scope = f"queue entry {queue_id}" if queue_id is not None else "entire mission queue"
    return _dump({"cancelled": scope})


@mcp.tool(
    annotations=ToolAnnotations(
        title="Read a PLC register",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_read_register(register_id: int) -> str:
    """Read one of the robot's 200 PLC registers (id 1-200) — the standard
    integration channel between a MiR and external equipment (doors,
    lifts, PLCs)."""
    body = await _robot("GET", f"/registers/{register_id}")
    return body if isinstance(body, str) else _dump(body)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Write a PLC register",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_write_register(register_id: int, value: float) -> str:
    """Write a value to a PLC register (id 1-200). On a real installation
    registers can trigger physical equipment — know what the register is
    wired to before writing."""
    body = await _robot("PUT", f"/registers/{register_id}", json_body={"value": value})
    return body if isinstance(body, str) else _dump(body)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Inject or clear emulator faults",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_manage_faults(
    faults: list[
        Literal[
            "emergency_stop",
            "error",
            "localization_lost",
            "battery_critical",
            "blocked_path",
            "mission_failure",
        ]
    ]
    | None = None,
) -> str:
    """EMULATOR ONLY — inject faults to test how an integration handles a
    misbehaving robot, or clear them all.

    Pass fault names to make them active (replaces the current set);
    pass an empty list or nothing to clear every fault. emergency_stop,
    error, and localization_lost freeze mission execution until cleared;
    blocked_path raises an active planner error while the robot keeps
    executing; mission_failure aborts the queue. error, localization_lost,
    and mission_failure also clear via mir_clear_error; emergency_stop,
    blocked_path, and battery_critical model a physical cause and clear
    only here. A real robot returns 404 — this surface does not exist on
    hardware.
    """
    if faults:
        body = await _robot("PUT", "/_emulator/faults", json_body={"faults": faults}, api=False)
    else:
        cleared = await _robot("DELETE", "/_emulator/faults", api=False)
        if isinstance(cleared, str) and cleared.startswith("Error:"):
            return cleared
        # DELETE answers with an empty body; report the observed fault state.
        body = await _robot("GET", "/_emulator/faults", api=False)
    return body if isinstance(body, str) else _dump(body)


# ---------------------------------------------------------------- fleet tools


@mcp.tool(
    annotations=ToolAnnotations(
        title="List the fleet's robots",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_fleet_robots(robot_id: str | None = None) -> str:
    """List the robots a MiR Fleet manages, or fetch one robot's live view
    by its robot-id (a guid). The fleet derives robot state from the robots
    themselves, so this is the authoritative multi-robot picture."""
    path = f"/robots/{robot_id}" if robot_id else "/robots"
    body = await _fleet("GET", path)
    return body if isinstance(body, str) else _dump(body)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Dispatch a fleet order",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=True,
    )
)
async def mir_fleet_dispatch(missions: list[str], robot_id: str | None = None) -> str:
    """Dispatch missions to the fleet as one serial order (POST
    /serial-order). Missions execute in the given sequence on a single
    robot — a specific robot_id, or the fleet's own choice when omitted.

    Each mission is a name (matched case-insensitively against GET
    /site/mission) or a guid. The order is atomic: if any mission is
    unknown, nothing is dispatched. Returns {"id": <serial-order id>} —
    track it with mir_fleet_order_status.
    """
    site = await _fleet("GET", "/site/mission")
    if isinstance(site, str):
        return site
    catalog = site.get("missions", []) if isinstance(site, dict) else []
    phases = []
    for wanted in missions:
        matches = [
            m
            for m in catalog
            if m.get("id") == wanted or str(m.get("name", "")).lower() == wanted.lower()
        ]
        if len(matches) != 1:
            available = ", ".join(f"{m.get('name')} ({m.get('id')})" for m in catalog) or "none"
            problem = "no site mission matches" if not matches else "ambiguous name"
            return f"Error: {problem} '{wanted}'. Available: {available}"
        phases.append({"mission-id": matches[0]["id"]})
    order: dict[str, Any] = {"phases": phases}
    if robot_id:
        order["robot-id"] = robot_id
    body = await _fleet("POST", "/serial-order", json_body={"serial-order": order})
    return body if isinstance(body, str) else _dump(body)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Check or abort a fleet order",
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_fleet_order_status(serial_order_id: str, abort: bool = False) -> str:
    """Read a serial order's live per-phase status, or abort it with
    abort=true (destructive: aborted orders stay aborted). Phase states are
    derived from the assigned robot's actual mission queue."""
    if abort:
        body = await _fleet("DELETE", f"/serial-order/{serial_order_id}")
        if isinstance(body, str) and body.startswith("Error:"):
            return body
        return _dump({"aborted": serial_order_id})
    body = await _fleet("GET", f"/serial-order/{serial_order_id}")
    return body if isinstance(body, str) else _dump(body)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Generate an HTML status report",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_generate_report(
    output_path: str,
    target: Literal["robot", "fleet"] = "robot",
    session_id: str | None = None,
) -> str:
    """Generate a self-contained HTML dashboard for the configured robot or
    fleet: current-status indicators, the daily trend, and a descriptive
    timeline of actions.

    Reads documented API endpoints only (robot: /status, /mission_queue,
    /log/error_reports, /statistics/distance; fleet: /robots, /order), so
    it is safe against real hardware — the only write is the local HTML
    file at output_path. Returns a JSON summary; open the file to view."""
    import os
    from pathlib import Path

    from mir_client.report import collect_report_async, render_report

    try:
        base = await (
            client.resolved_robot_base() if target == "robot" else client.resolved_fleet_base()
        )
    except client.TargetResolutionError as exc:
        return str(exc)
    kwargs: dict[str, Any] = {"transport": client.TRANSPORT} if client.TRANSPORT else {}
    try:
        data = await collect_report_async(
            base,
            username=os.environ.get("MIR_USERNAME", "distributor"),
            password=os.environ.get("MIR_PASSWORD", "distributor"),
            api_key=os.environ.get("MIR_API_KEY", "distributor"),
            session_id=session_id or os.environ.get("MIR_SESSION") or None,
            **kwargs,
        )
    except Exception as exc:  # unreachable host, auth, kind gate — all actionable
        return (
            f"Error: report collection from {base} failed: {exc}. Check the URL is a "
            "robot or fleet (mir_server_info) and credentials (MIR_USERNAME/"
            "MIR_PASSWORD or MIR_API_KEY)."
        )
    Path(output_path).write_text(render_report(data))
    return _dump(
        {
            "path": output_path,
            "kind": data["kind"],
            "version": data.get("version"),
            "robots": [
                {"name": r["name"], "battery": r["battery"], "state": r["state"]}
                for r in data["robots"]
            ],
            "timeline_entries": len(data["timeline"]),
            "trend_days": len(data["trend"]),
        }
    )


def main() -> int:
    """stdio entry point: `mir-mcp` (or `uv run mir-mcp`)."""
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
