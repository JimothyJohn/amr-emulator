"""MCP server: natural-language control of MiR robots and fleets.

Every tool wraps the documented MiR REST API (robot ``/api/v2.0.0``, fleet
``/api/v1``) plus the emulator-only test surfaces under ``/_emulator/*``.

Agent interface (MCP 2.0 native):

- Tools return **structured content** (typed dicts with advertised output
  schemas), so agents consume fields, not prose.
- Failures raise :class:`ToolError` — the ``isError`` channel — with the fix
  spelled out in the message, so agents can branch on failure without
  parsing happy-path text for "Error:" prefixes.
- Where the connected client supports **elicitation**, destructive or
  ambiguous calls ask instead of guessing: clearing the whole mission queue
  asks for confirmation, and an ambiguous mission name asks which one was
  meant. Clients without elicitation keep the 1.x behavior.
- ``mir_wait_for`` turns agent-side status polling into one server-side
  wait with **progress notifications** and a transition log.
- The live status is also a **resource** (``mir://robot/status``);
  ``mir_wait_for`` emits ``notifications/resources/updated`` whenever the
  observed state changes, so subscribed clients ride the push channel.
"""

from __future__ import annotations

import asyncio
import json
from typing import Annotated, Any, Literal

import httpx
from mcp.server.caching import CacheHint
from mcp.server.mcpserver import (
    Context,
    Elicit,
    ElicitationResult,
    MCPServer,
    Resolve,
)
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, create_model

from mir_mcp import client

STATUS_RESOURCE_URI = "mir://robot/status"

INSTRUCTIONS = """\
Control MiR robots and fleets through their documented REST APIs. Works
identically against the mir-emulator and real hardware — assume writes move
a physical vehicle unless mir_server_info says otherwise.

Workflow: call mir_server_info first to learn what MIR_ROBOT_URL /
MIR_FLEET_URL point at (robot, fleet, or multi-version dispatcher) and the
software version; if there is no configured target, mir_discover_robots
scans the network. Mission guids come from mir_list_missions — never invent
one. To follow long-running work, prefer one mir_wait_for call (server-side
wait with progress) over polling mir_robot_status in a loop; the live
status is also readable as the mir://robot/status resource. Tools raise
errors whose messages state the fix (wrong credentials, unreachable host,
unknown mission) — read them before retrying. mir_manage_faults exists only
on the emulator and returns an error on real hardware.
"""

mcp = MCPServer(
    "mir_mcp",
    instructions=INSTRUCTIONS,
    # The tool and resource sets are static for a server's lifetime.
    cache_hints={
        "tools/list": CacheHint(ttl_ms=3_600_000),
        "resources/list": CacheHint(ttl_ms=3_600_000),
    },
)

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

WAIT_CONDITIONS = {
    "mission_queue_idle": "no mission queue entry is Pending or Executing",
    "state_ready": "state_id == 3 (Ready)",
    "state_executing": "state_id == 5 (Executing)",
    "error_cleared": "the errors array is empty",
    "battery_above": "battery_percentage > threshold",
}


def _as_list(value: Any) -> list:
    """MiR specs declare some list endpoints with the element's object schema,
    and servers differ on which shape they answer with — accept both (same
    defense as mir_client.report._as_list)."""
    if isinstance(value, list):
        return value
    return [value] if isinstance(value, dict) else []


def _trim_status(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: doc[k] for k in STATUS_FIELDS if k in doc}


async def _robot(method: str, path: str, *, json_body: Any = None, api: bool = True) -> Any:
    """Run one robot call; the body on success, ToolError with the fix on failure."""
    try:
        status, body = await client.robot_request(method, path, json=json_body, api=api)
    except client.TargetResolutionError as exc:
        raise ToolError(str(exc)) from exc
    except httpx.HTTPError as exc:
        raise ToolError(client.describe_connection_error(exc, client.robot_base_url())) from exc
    if status >= 400:
        raise ToolError(client.describe_http_error(status, body, "robot"))
    return body


async def _fleet(method: str, path: str, *, json_body: Any = None) -> Any:
    try:
        status, body = await client.fleet_request(method, path, json=json_body)
    except client.TargetResolutionError as exc:
        raise ToolError(str(exc)) from exc
    except httpx.HTTPError as exc:
        raise ToolError(client.describe_connection_error(exc, client.fleet_base_url())) from exc
    if status >= 400:
        raise ToolError(client.describe_http_error(status, body, "fleet"))
    return body


def _can_elicit(ctx: Context | None) -> bool:
    caps = ctx.client_capabilities if ctx is not None else None
    return caps is not None and caps.elicitation is not None


class _ConfirmClear(BaseModel):
    confirm: bool = Field(description="Clear the entire mission queue?")


async def _lookup_mission(name_or_guid: str) -> tuple[list[dict[str, Any]], str]:
    """(matching missions, formatted list of everything that exists)."""
    entries = _as_list(await _robot("GET", "/missions"))
    exact = [m for m in entries if m.get("guid") == name_or_guid]
    named = [m for m in entries if str(m.get("name", "")).lower() == name_or_guid.lower()]
    available = ", ".join(f"{m.get('name')} ({m.get('guid')})" for m in entries) or "none"
    return (exact or named), available


async def _mission_or_error(name_or_guid: str) -> dict[str, Any]:
    """Non-interactive resolution: exactly one match or a ToolError."""
    matches, available = await _lookup_mission(name_or_guid)
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ToolError(
            f"Error: no mission named or with guid '{name_or_guid}'. Available: {available}"
        )
    raise ToolError(f"Error: '{name_or_guid}' is ambiguous. Matches: {available}")


async def _mission_choice(mission: str, ctx: Context) -> Any:
    """Resolver for mir_queue_mission's target.

    Unambiguous -> the mission document. Unknown -> ToolError naming what
    exists. Ambiguous -> ask which guid was meant (Elicit); clients without
    elicitation get the listing error instead. The framework replays the
    elicited answer across input_required rounds, so the question is asked
    once.
    """
    matches, available = await _lookup_mission(mission)
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ToolError(f"Error: no mission named or with guid '{mission}'. Available: {available}")
    if not _can_elicit(ctx):
        raise ToolError(f"Error: '{mission}' is ambiguous. Matches: {available}")
    guids = tuple(str(m.get("guid")) for m in matches)
    labels = "; ".join(f"{m.get('guid')}: {m.get('name')}" for m in matches)
    choose = create_model(
        "ChooseMission",
        guid=(Literal[guids], Field(description=f"Which mission did you mean? {labels}")),  # ty: ignore[invalid-type-form]
    )
    return Elicit(f"'{mission}' matches {len(matches)} missions. Which one should run?", choose)


async def _confirm_queue_clear(queue_id: int | None, ctx: Context) -> Any:
    """Resolver: confirmation for clearing the whole mission queue.

    Single-entry cancels and clients without elicitation skip the question
    (auto-confirm — the pre-elicitation contract, guarded by the tool's
    destructive_hint).
    """
    if queue_id is not None or not _can_elicit(ctx):
        # A plain return is wrapped as an accepted outcome for the consumer.
        return _ConfirmClear(confirm=True)
    pending = [
        e
        for e in _as_list(await _robot("GET", "/mission_queue"))
        if e.get("state") in ("Pending", "Executing")
    ]
    return Elicit(
        f"Clear the entire mission queue ({len(pending)} entries still "
        "pending or executing)? This cannot be undone.",
        _ConfirmClear,
    )


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


@mcp.resource(
    STATUS_RESOURCE_URI,
    name="robot-status",
    title="Live MiR robot status",
    description=(
        "The connected robot's live status (state, battery, position, mission, "
        "errors) as JSON. mir_wait_for announces updates to this resource "
        "whenever it observes the state change."
    ),
    mime_type="application/json",
)
async def robot_status_resource() -> str:
    status = _trim_status(await _robot("GET", "/status"))
    return json.dumps(status, indent=1, sort_keys=True)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Identify the connected MiR target",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_server_info() -> dict[str, Any]:
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
    return doc


@mcp.tool(
    annotations=ToolAnnotations(
        title="Discover MiR robots on the network",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_discover_robots(hosts: list[str] | None = None) -> dict[str, Any]:
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
        raise ToolError(f"Error: {exc}") from exc
    except OSError as exc:
        raise ToolError(f"Error: network scan failed ({type(exc).__name__}: {exc}).") from exc
    if not found:
        where = ", ".join(hosts) if hosts else "the local /24"
        return {
            "found": [],
            "count": 0,
            "scanned": where,
            "hint": (
                "No MiR robots or fleets answered. Check you are on the robot's "
                "network, or start an emulator with `uv run mir-emulator`."
            ),
        }
    return {"found": found, "count": len(found)}


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
async def mir_robot_status() -> dict[str, Any]:
    """Read the robot's live status: state, battery, position, current
    mission, and any errors.

    Returns robot_name, state_id/state_text (3 Ready, 4 Pause, 5 Executing,
    10 Emergency stop, 11 Manual control, 12 Error), battery_percentage,
    position {x, y, orientation}, mission_text, mission_queue_id and
    errors[]. Call this first to verify connectivity, and after any state
    change to confirm it took effect. To wait on a state, prefer
    mir_wait_for over polling this tool.
    """
    return _trim_status(await _robot("GET", "/status"))


@mcp.tool(
    annotations=ToolAnnotations(
        title="Set robot state (ready / pause / manual)",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_set_robot_state(state: Literal["ready", "pause", "manual_control"]) -> dict[str, Any]:
    """Pause the robot, resume it, or hand it to manual control.

    'pause' freezes mission execution in place; 'ready' resumes exactly
    where it stopped; 'manual_control' releases the drive to a human with
    the joystick. Maps to the documented PUT /status state_id (3/4/11).
    Returns the resulting status so the caller sees the observed state.
    """
    return _trim_status(await _robot("PUT", "/status", json_body={"state_id": STATE_IDS[state]}))


@mcp.tool(
    annotations=ToolAnnotations(
        title="Clear robot error state",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_clear_error() -> dict[str, Any]:
    """Acknowledge and clear the robot's error state (PUT /status
    {"clear_error": true}), the documented recovery for resettable errors.

    An emergency stop cannot be cleared this way — on a real robot the
    physical button must be released; on the emulator use mir_manage_faults.
    Returns the resulting status.
    """
    return _trim_status(await _robot("PUT", "/status", json_body={"clear_error": True}))


@mcp.tool(
    annotations=ToolAnnotations(
        title="List mission definitions",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_list_missions() -> dict[str, Any]:
    """List the missions defined on the robot as {missions: [{guid, name}]}.

    Mission guids come from here — never guess one. Use the guid (or the
    unique name) with mir_queue_mission.
    """
    entries = _as_list(await _robot("GET", "/missions"))
    return {"missions": [{"guid": m.get("guid"), "name": m.get("name")} for m in entries]}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Queue a mission",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=True,
    )
)
async def mir_queue_mission(
    mission: str,
    wait_seconds: int = 0,
    chosen: Annotated[Any, Resolve(_mission_choice)] = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Queue a mission for execution, by name (case-insensitive) or guid.

    The robot works the queue in order: Pending -> Executing -> Done. With
    wait_seconds > 0, polls the queue entry (reporting progress) and
    returns once it reaches Done/Aborted or the wait expires — the returned
    'state' is always the last observed one. If the name is ambiguous and
    the client supports elicitation, you are asked which mission was meant.
    Against a real robot this physically moves the vehicle.
    """
    if chosen is None:
        # Called outside the MCP framework (no resolver ran): resolve
        # non-interactively.
        resolved = await _mission_or_error(mission)
    elif isinstance(chosen, BaseModel):
        # The elicited answer: a guid picked from the ambiguous matches.
        guid = chosen.guid  # type: ignore[attr-defined]
        entries = _as_list(await _robot("GET", "/missions"))
        resolved = next(m for m in entries if str(m.get("guid")) == guid)
    else:
        resolved = chosen
    entry = await _robot("POST", "/mission_queue", json_body={"mission_id": resolved["guid"]})
    wait = min(wait_seconds, 300)
    started = asyncio.get_event_loop().time()
    while wait_seconds and entry.get("state") not in ("Done", "Aborted"):
        elapsed = asyncio.get_event_loop().time() - started
        if elapsed >= wait:
            break
        if ctx is not None:
            await ctx.report_progress(
                min(elapsed, wait), wait, f"queue entry {entry.get('id')}: {entry.get('state')}"
            )
        await asyncio.sleep(0.5)
        entry = await _robot("GET", f"/mission_queue/{entry.get('id')}")
    return {"mission": resolved["name"], "queue_entry": entry}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Show the mission queue",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_mission_queue(queue_id: int | None = None) -> dict[str, Any]:
    """Read the mission queue (all entries) or one entry by its integer id.

    Each entry carries id, state (Pending/Executing/Done/Aborted) and
    timestamps. To wait for the queue to drain, prefer mir_wait_for
    ('mission_queue_idle') over polling this tool.
    """
    if queue_id is not None:
        return {"entry": await _robot("GET", f"/mission_queue/{queue_id}")}
    return {"entries": _as_list(await _robot("GET", "/mission_queue"))}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Cancel queued missions",
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_cancel_missions(
    queue_id: int | None = None,
    confirmation: Annotated[  # ty: ignore[invalid-parameter-default]
        ElicitationResult[_ConfirmClear], Resolve(_confirm_queue_clear)
    ] = None,
) -> dict[str, Any]:
    """Cancel one queued mission by id, or the entire queue when no id is
    given. Destructive: a cleared queue cannot be restored — re-queue the
    missions if needed. Clearing the whole queue asks for confirmation
    when the client supports elicitation; a decline cancels nothing.
    """
    if confirmation is not None and (
        confirmation.action != "accept" or not confirmation.data.confirm
    ):
        return {"cancelled": None, "declined": True}
    path = f"/mission_queue/{queue_id}" if queue_id is not None else "/mission_queue"
    await _robot("DELETE", path)
    scope = f"queue entry {queue_id}" if queue_id is not None else "entire mission queue"
    return {"cancelled": scope}


@mcp.tool(
    annotations=ToolAnnotations(
        title="Wait for a robot condition",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_wait_for(
    condition: Literal[
        "mission_queue_idle", "state_ready", "state_executing", "error_cleared", "battery_above"
    ],
    threshold: float | None = None,
    timeout_seconds: float = 60,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Wait server-side until the robot reaches a condition — one call
    instead of an agent-side polling loop.

    Conditions: mission_queue_idle (no Pending/Executing entries),
    state_ready, state_executing, error_cleared, battery_above (needs
    threshold, in %). Polls twice a second up to timeout_seconds (max 300),
    reporting progress and announcing mir://robot/status updates on every
    observed state change. Returns whether the condition was met, the
    elapsed time, the state transitions observed while waiting, and the
    final trimmed status.
    """
    if condition == "battery_above" and threshold is None:
        raise ToolError("Error: condition 'battery_above' needs a threshold (battery %).")
    needed = float(threshold if threshold is not None else 0.0)
    timeout = min(timeout_seconds, 300.0)

    async def met(status: dict[str, Any]) -> bool:
        if condition == "state_ready":
            return status.get("state_id") == 3
        if condition == "state_executing":
            return status.get("state_id") == 5
        if condition == "error_cleared":
            return not status.get("errors")
        if condition == "battery_above":
            return float(status.get("battery_percentage", 0.0)) > needed
        queue = _as_list(await _robot("GET", "/mission_queue"))
        return not any(e.get("state") in ("Pending", "Executing") for e in queue)

    loop = asyncio.get_event_loop()
    started = loop.time()
    transitions: list[dict[str, Any]] = []
    last_state: str | None = None
    while True:
        status = _trim_status(await _robot("GET", "/status"))
        elapsed = round(loop.time() - started, 2)
        if status.get("state_text") != last_state:
            if last_state is not None and ctx is not None:
                await ctx.notify_resource_updated(STATUS_RESOURCE_URI)
            transitions.append({"at_seconds": elapsed, "state_text": status.get("state_text")})
            last_state = status.get("state_text")
        if await met(status):
            return {
                "met": True,
                "condition": condition,
                "elapsed_seconds": elapsed,
                "transitions": transitions,
                "status": status,
            }
        if elapsed >= timeout:
            return {
                "met": False,
                "condition": condition,
                "elapsed_seconds": elapsed,
                "transitions": transitions,
                "status": status,
                "hint": f"condition means: {WAIT_CONDITIONS[condition]}",
            }
        if ctx is not None:
            await ctx.report_progress(
                min(elapsed, timeout),
                timeout,
                f"waiting for {condition}; state={status.get('state_text')}",
            )
        await asyncio.sleep(0.5)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Read a PLC register",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_read_register(register_id: int) -> dict[str, Any]:
    """Read one of the robot's 200 PLC registers (id 1-200) — the standard
    integration channel between a MiR and external equipment (doors,
    lifts, PLCs)."""
    return await _robot("GET", f"/registers/{register_id}")


@mcp.tool(
    annotations=ToolAnnotations(
        title="Write a PLC register",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_write_register(register_id: int, value: float) -> dict[str, Any]:
    """Write a value to a PLC register (id 1-200). On a real installation
    registers can trigger physical equipment — know what the register is
    wired to before writing."""
    return await _robot("PUT", f"/registers/{register_id}", json_body={"value": value})


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
) -> dict[str, Any]:
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
        return await _robot("PUT", "/_emulator/faults", json_body={"faults": faults}, api=False)
    await _robot("DELETE", "/_emulator/faults", api=False)
    # DELETE answers with an empty body; report the observed fault state.
    return await _robot("GET", "/_emulator/faults", api=False)


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
async def mir_fleet_robots(robot_id: str | None = None) -> dict[str, Any]:
    """List the robots a MiR Fleet manages, or fetch one robot's live view
    by its robot-id (a guid). The fleet derives robot state from the robots
    themselves, so this is the authoritative multi-robot picture."""
    if robot_id:
        return await _fleet("GET", f"/robots/{robot_id}")
    return await _fleet("GET", "/robots")


@mcp.tool(
    annotations=ToolAnnotations(
        title="Dispatch a fleet order",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=True,
    )
)
async def mir_fleet_dispatch(missions: list[str], robot_id: str | None = None) -> dict[str, Any]:
    """Dispatch missions to the fleet as one serial order (POST
    /serial-order). Missions execute in the given sequence on a single
    robot — a specific robot_id, or the fleet's own choice when omitted.

    Each mission is a name (matched case-insensitively against GET
    /site/mission) or a guid. The order is atomic: if any mission is
    unknown, nothing is dispatched. Returns {"id": <serial-order id>} —
    track it with mir_fleet_order_status.
    """
    site = await _fleet("GET", "/site/mission")
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
            raise ToolError(f"Error: {problem} '{wanted}'. Available: {available}")
        phases.append({"mission-id": matches[0]["id"]})
    order: dict[str, Any] = {"phases": phases}
    if robot_id:
        order["robot-id"] = robot_id
    return await _fleet("POST", "/serial-order", json_body={"serial-order": order})


@mcp.tool(
    annotations=ToolAnnotations(
        title="Check or abort a fleet order",
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    )
)
async def mir_fleet_order_status(serial_order_id: str, abort: bool = False) -> dict[str, Any]:
    """Read a serial order's live per-phase status, or abort it with
    abort=true (destructive: aborted orders stay aborted). Phase states are
    derived from the assigned robot's actual mission queue."""
    if abort:
        await _fleet("DELETE", f"/serial-order/{serial_order_id}")
        return {"aborted": serial_order_id}
    return await _fleet("GET", f"/serial-order/{serial_order_id}")


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
) -> dict[str, Any]:
    """Generate a self-contained HTML dashboard for the configured robot or
    fleet: current-status indicators, the daily trend, and a descriptive
    timeline of actions.

    Reads documented API endpoints only (robot: /status, /mission_queue,
    /log/error_reports, /statistics/distance; fleet: /robots, /order), so
    it is safe against real hardware — the only write is the local HTML
    file at output_path. Returns a summary; open the file to view."""
    import os
    from pathlib import Path

    from mir_client.report import collect_report_async, render_report

    try:
        base = await (
            client.resolved_robot_base() if target == "robot" else client.resolved_fleet_base()
        )
    except client.TargetResolutionError as exc:
        raise ToolError(str(exc)) from exc
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
        raise ToolError(
            f"Error: report collection from {base} failed: {exc}. Check the URL is a "
            "robot or fleet (mir_server_info) and credentials (MIR_USERNAME/"
            "MIR_PASSWORD or MIR_API_KEY)."
        ) from exc
    Path(output_path).write_text(render_report(data))
    return {
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


def main() -> int:
    """stdio entry point: `mir-mcp` (or `uv run mir-mcp`)."""
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
