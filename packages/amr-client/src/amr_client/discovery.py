"""Connect-time discovery: ask the target what it is and which MiR software
version it runs, instead of requiring the user to install or guess one.

The MiR path version never moved (robots serve ``/api/v2.0.0`` from software
2.x through 3.x, fleets serve ``/api/v1``), so "which API version" really
means "which software version's surface". The handshake probes, first hit
wins:

1. ``GET /healthz``                — the multi-version demo dispatcher's
   manifest (``{"versions": [...], "fleet_versions": [...]}``); pick a
   version mount from it.
2. ``GET /``                       — the emulator's JSON index
   (``kind`` + ``emulated_mir_version`` / ``emulated_fleet_version``).
3. ``GET /api/v1/system/version``  — the official Fleet endpoint; works on
   real MiR Fleet installations.
4. ``GET /swagger.json``           — ``info.version`` on a robot serving its
   own spec.
5. ``GET /api/v2.0.0/status``      — a robot that won't say its version
   (real hardware with no open surfaces); 200/401 proves the API family,
   the version stays unknown.

Every probe is safe: unauthenticated GETs only (probe 3 sends the fleet
API key header, read-only either way).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any

import httpx

from amr_client import _provenance as provenance

ROBOT_API_PREFIX = "/api/v2.0.0"
FLEET_API_PREFIX = "/api/v1"
DEFAULT_TIMEOUT_S = 5.0

# Fields a real MiR /status always carries; used to tell an authentic robot
# from a server that simply answers 200 to every path.
_ROBOT_STATUS_MARKERS = (
    "state_id",
    "state_text",
    "battery_percentage",
    "robot_name",
    "mission_queue_id",
    "serial_number",
)


class DiscoveryError(RuntimeError):
    """The target could not be reached or does not speak a MiR API."""


@dataclass(frozen=True)
class ServerInfo:
    """What the connect-time handshake learned about a target."""

    kind: str  # "robot" | "fleet" | "dispatcher"
    version: str | None  # MiR software / fleet version; None if the target won't say
    base_url: str  # root to hand to robot_client()/fleet_client()
    api_prefix: str  # "/api/v2.0.0", "/api/v1", or "" for a dispatcher
    versions: tuple[str, ...] = ()  # dispatcher only: robot versions served
    fleet_versions: tuple[str, ...] = ()  # dispatcher only: fleet versions served
    latest: str | None = field(default=None)  # dispatcher only: newest robot version


def _json_or_none(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _str_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return tuple(value)
    return ()


def _probe_plan(api_key: str) -> list[tuple[str, str, dict[str, str]]]:
    return [
        ("healthz", "/healthz", {}),
        ("index", "/", {"Accept": "application/json"}),
        ("fleet_version", f"{FLEET_API_PREFIX}/system/version", {"x-api-key": api_key}),
        ("swagger", "/swagger.json", {}),
        ("robot_status", f"{ROBOT_API_PREFIX}/status", {}),
    ]


def _interpret(probe: str, status: int, doc: Any, base_url: str) -> ServerInfo | None:
    """Pure classification of one probe response; None means keep probing."""
    if probe == "robot_status":
        # 401 at exactly /api/v2.0.0/status is a strong MiR signal (a bare
        # web server does not auth-wall that path). A 200 only counts if the
        # body is actually a MiR status document — a server that answers 200
        # to every path must not be mistaken for a robot. Version stays
        # unknown either way: real robots don't publish one here.
        if status == 401:
            return ServerInfo("robot", None, base_url, ROBOT_API_PREFIX)
        if status == 200 and isinstance(doc, dict) and any(k in doc for k in _ROBOT_STATUS_MARKERS):
            return ServerInfo("robot", None, base_url, ROBOT_API_PREFIX)
        return None
    if status != 200 or not isinstance(doc, dict):
        return None
    if probe == "healthz":
        versions = _str_tuple(doc.get("versions"))
        if not versions:
            return None
        return ServerInfo(
            "dispatcher",
            None,
            base_url,
            "",
            versions=versions,
            fleet_versions=_str_tuple(doc.get("fleet_versions")),
            latest=doc.get("latest") if isinstance(doc.get("latest"), str) else versions[0],
        )
    if probe == "index":
        robot_version = doc.get("emulated_mir_version")
        if doc.get("kind") == "robot" or isinstance(robot_version, str):
            prefix = doc.get("base_path")
            return ServerInfo(
                "robot",
                robot_version if isinstance(robot_version, str) else None,
                base_url,
                prefix if isinstance(prefix, str) else ROBOT_API_PREFIX,
            )
        fleet_version = doc.get("emulated_fleet_version")
        if doc.get("kind") == "fleet" or isinstance(fleet_version, str):
            return ServerInfo(
                "fleet",
                fleet_version if isinstance(fleet_version, str) else None,
                base_url,
                FLEET_API_PREFIX,
            )
        return None
    if probe == "fleet_version":
        version = doc.get("version")
        if isinstance(version, str) and version:
            return ServerInfo("fleet", version, base_url, FLEET_API_PREFIX)
        return None
    if probe == "swagger":
        info = doc.get("info")
        if (doc.get("swagger") or doc.get("openapi")) and isinstance(info, dict):
            version = info.get("version")
            if isinstance(version, str) and version:
                return ServerInfo("robot", version, base_url, ROBOT_API_PREFIX)
        return None
    return None


def _unidentified(
    base_url: str, saw_response: bool, last_error: Exception | None
) -> DiscoveryError:
    if saw_response:
        return DiscoveryError(
            f"{base_url} answered, but no probe identified a MiR robot, fleet, or "
            "multi-version dispatcher (tried /healthz, /, /api/v1/system/version, "
            "/swagger.json, /api/v2.0.0/status)"
        )
    error = DiscoveryError(f"cannot reach {base_url}: {last_error}")
    error.__cause__ = last_error
    return error


def detect_server(
    base_url: str,
    *,
    api_key: str = "distributor",
    timeout: float = DEFAULT_TIMEOUT_S,
    **httpx_kwargs: Any,
) -> ServerInfo:
    """Identify whatever is at *base_url* (robot / fleet / dispatcher) and its
    software version, without credentials and without changing any state."""
    base = base_url.rstrip("/")
    saw_response, last_error = False, None
    with httpx.Client(timeout=timeout, **httpx_kwargs) as http:
        for probe, path, headers in _probe_plan(api_key):
            try:
                response = http.get(base + path, headers=headers)
            except httpx.HTTPError as exc:
                last_error = exc
                continue
            saw_response = True
            info = _interpret(probe, response.status_code, _json_or_none(response), base)
            if info is not None:
                return info
    raise _unidentified(base, saw_response, last_error)


async def detect_server_async(
    base_url: str,
    *,
    api_key: str = "distributor",
    timeout: float = DEFAULT_TIMEOUT_S,
    **httpx_kwargs: Any,
) -> ServerInfo:
    """Async twin of :func:`detect_server` (same probes, same result)."""
    base = base_url.rstrip("/")
    saw_response, last_error = False, None
    async with httpx.AsyncClient(timeout=timeout, **httpx_kwargs) as http:
        for probe, path, headers in _probe_plan(api_key):
            try:
                response = await http.get(base + path, headers=headers)
            except httpx.HTTPError as exc:
                last_error = exc
                continue
            saw_response = True
            info = _interpret(probe, response.status_code, _json_or_none(response), base)
            if info is not None:
                return info
    raise _unidentified(base, saw_response, last_error)


def _components_differ(a: str, b: str, depth: int) -> bool:
    return a.split(".")[:depth] != b.split(".")[:depth]


def _warn_if_generation_gap(info: ServerInfo) -> None:
    """The generated models are pinned to one spec; surface a real gap.

    Robots break at the major (2.x vs 3.x); fleets are all 1.x, so the minor
    is where surfaces diverge (e.g. /robots only exists from 1.4.0 on).
    """
    if info.version is None:
        return
    if info.kind == "robot" and _components_differ(info.version, provenance.ROBOT_VERSION, 1):
        warnings.warn(
            f"this client was generated from the MiR {provenance.ROBOT_VERSION} spec, but "
            f"the robot reports {info.version}; endpoints and fields may differ — compare "
            "with the emulator's /_emulator/diff",
            UserWarning,
            stacklevel=3,
        )
    if info.kind == "fleet" and _components_differ(info.version, provenance.FLEET_VERSION, 2):
        warnings.warn(
            f"this client was generated from the MiR Fleet {provenance.FLEET_VERSION} spec, "
            f"but the fleet reports {info.version}; endpoints may differ",
            UserWarning,
            stacklevel=3,
        )
