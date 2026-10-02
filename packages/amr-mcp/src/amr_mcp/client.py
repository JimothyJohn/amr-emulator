"""HTTP plumbing shared by every MCP tool.

Configuration is environment-driven so the same server binary points at an
emulator on localhost or a real robot on the shop floor:

- ``AMR_ROBOT_URL``  — robot base URL (default ``http://127.0.0.1:8080``)
- ``AMR_FLEET_URL``  — fleet base URL (default: same as ``AMR_ROBOT_URL``)
- ``AMR_USERNAME`` / ``AMR_PASSWORD`` — robot account (default the MiR
  factory account ``distributor``/``distributor``)
- ``AMR_API_KEY``    — fleet ``x-api-key`` (default ``distributor``)
- ``AMR_SESSION``    — optional ``X-AMR-Session`` id for emulator state
  isolation (emulator-only; harmless against real hardware)
- ``AMR_VERSION`` / ``AMR_FLEET_VERSION`` — optional MiR software version to
  pin when the URL points at a multi-version dispatcher (the public demo);
  default is whatever the dispatcher reports as newest

Version handling is a connect-time handshake, not configuration: the first
request probes the target (``/healthz`` manifest, ``/`` index, the official
fleet ``/api/v1/system/version``, ``/swagger.json``, then a bare
``/api/v2.0.0/status``) to learn what it is and which software version it
runs, and caches the answer per base URL.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import hashlib
import ipaddress
import os
import socket
from typing import Any

import httpx

ROBOT_API_PREFIX = "/api/v2.0.0"
FLEET_API_PREFIX = "/api/v1"
REQUEST_TIMEOUT_S = 15.0

# Fields a real MiR /status always carries; used to tell an authentic robot
# from a server that answers 200 to every path.
_ROBOT_STATUS_MARKERS = (
    "state_id",
    "state_text",
    "battery_percentage",
    "robot_name",
    "mission_queue_id",
    "serial_number",
)

# Tests inject an in-process ASGI transport here; production uses real TCP.
TRANSPORT: httpx.AsyncBaseTransport | None = None


def robot_base_url() -> str:
    return os.environ.get("AMR_ROBOT_URL", "http://127.0.0.1:8080").rstrip("/")


def fleet_base_url() -> str:
    return os.environ.get("AMR_FLEET_URL", robot_base_url()).rstrip("/")


def mir_basic_token(username: str, password: str) -> str:
    """MiR Basic auth: the password travels as its lowercase SHA-256 hex digest."""
    digest = hashlib.sha256(password.encode()).hexdigest()
    return base64.b64encode(f"{username}:{digest}".encode()).decode()


def _session_headers() -> dict[str, str]:
    session = os.environ.get("AMR_SESSION", "")
    return {"X-AMR-Session": session} if session else {}


def robot_headers() -> dict[str, str]:
    username = os.environ.get("AMR_USERNAME", "distributor")
    password = os.environ.get("AMR_PASSWORD", "distributor")
    return {
        "Authorization": f"Basic {mir_basic_token(username, password)}",
        **_session_headers(),
    }


def fleet_headers() -> dict[str, str]:
    return {
        "x-api-key": os.environ.get("AMR_API_KEY", "distributor"),
        **_session_headers(),
    }


async def _request(
    base_url: str,
    headers: dict[str, str],
    method: str,
    path: str,
    *,
    json: Any = None,
    params: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    async with httpx.AsyncClient(
        transport=TRANSPORT, timeout=REQUEST_TIMEOUT_S, headers=headers
    ) as client:
        response = await client.request(method, f"{base_url}{path}", json=json, params=params)
    try:
        body = response.json()
    except ValueError:
        body = response.text
    return response.status_code, body


class TargetResolutionError(RuntimeError):
    """A pinned AMR_VERSION/AMR_FLEET_VERSION the target does not serve."""


# Connect-time handshake results, keyed by base URL. Only successful
# identifications are cached, so a target that boots late is re-probed.
_detected: dict[str, dict[str, Any]] = {}


async def _probe(base_url: str, path: str, headers: dict[str, str] | None = None):
    try:
        return await _request(base_url, headers or {}, "GET", path)
    except httpx.HTTPError:
        return None


async def _identify(base_url: str) -> dict[str, Any] | None:
    """One pass of the discovery handshake; None means nothing MiR answered.

    Same probe order as ``amr_client.discovery`` — the two implementations
    share the protocol, not code, so amr-mcp stays installable on its own.
    """
    hit = await _probe(base_url, "/healthz")
    if hit and hit[0] == 200 and isinstance(hit[1], dict):
        versions = hit[1].get("versions")
        if isinstance(versions, list) and versions:
            fleet_versions = [str(v) for v in hit[1].get("fleet_versions") or []]
            return {
                "kind": "dispatcher",
                "version": None,
                "versions": [str(v) for v in versions],
                "latest": str(hit[1].get("latest") or versions[0]),
                "fleet_versions": fleet_versions,
                "fleet_latest": str(hit[1].get("fleet_latest") or "")
                or (fleet_versions[0] if fleet_versions else None),
            }
    hit = await _probe(base_url, "/", headers={"Accept": "application/json"})
    if hit and hit[0] == 200 and isinstance(hit[1], dict):
        doc = hit[1]
        if doc.get("kind") == "robot" or "emulated_mir_version" in doc:
            return {"kind": "robot", "version": doc.get("emulated_mir_version")}
        if doc.get("kind") == "fleet" or "emulated_fleet_version" in doc:
            return {"kind": "fleet", "version": doc.get("emulated_fleet_version")}
    hit = await _probe(base_url, f"{FLEET_API_PREFIX}/system/version", headers=fleet_headers())
    if (
        hit
        and hit[0] == 200
        and isinstance(hit[1], dict)
        and isinstance(hit[1].get("version"), str)
    ):
        return {"kind": "fleet", "version": hit[1]["version"]}
    hit = await _probe(base_url, "/swagger.json")
    if hit and hit[0] == 200 and isinstance(hit[1], dict):
        info = hit[1].get("info")
        has_spec_marker = hit[1].get("swagger") or hit[1].get("openapi")
        if has_spec_marker and isinstance(info, dict) and isinstance(info.get("version"), str):
            return {"kind": "robot", "version": info["version"]}
    hit = await _probe(base_url, f"{ROBOT_API_PREFIX}/status")
    if hit and hit[0] == 401:
        # A 401 at exactly this path is a strong MiR signal (auth wall).
        return {"kind": "robot", "version": None}
    if (
        hit
        and hit[0] == 200
        and isinstance(hit[1], dict)
        and any(k in hit[1] for k in _ROBOT_STATUS_MARKERS)
    ):
        # 200 only counts with a real status body — a server that 200s every
        # path must not read as a robot. Version stays unknown; robots don't
        # publish one here.
        return {"kind": "robot", "version": None}
    return None


SCAN_PORTS: tuple[int, ...] = (80, 8080)  # real robots on 80, emulator on 8080
_SCAN_MAX_CANDIDATES = 1024


def _local_ipv4() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 9))  # TEST-NET-1: routes, never sends
            return str(probe.getsockname()[0])
    except OSError:
        return None


def _expand_hosts(spec: list[str]) -> list[str]:
    hosts: list[str] = []
    for item in spec:
        if "/" in item:
            hosts.extend(str(a) for a in ipaddress.ip_network(item, strict=False).hosts())
        else:
            hosts.append(item)
    return list(dict.fromkeys(hosts))


async def _tcp_accepts(host: str, port: int, timeout: float) -> bool:
    try:
        _reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
    except (TimeoutError, OSError):
        return False
    writer.close()
    with contextlib.suppress(Exception):
        await writer.wait_closed()
    return True


async def scan_for_targets(
    hosts: list[str] | None = None,
    *,
    ports: tuple[int, ...] | None = None,
    connect_timeout: float = 0.5,
    identify_timeout: float = 3.0,
    concurrency: int = 128,
) -> list[dict[str, Any]]:
    """Sweep the network for MiR targets. Returns one dict per identified
    robot/fleet/dispatcher: url, host, port, kind, version.

    *hosts* accepts IPs, hostnames, and CIDR blocks; None scans the local
    /24. Each candidate gets a cheap TCP connect, then the same handshake
    the tools use — under a hard deadline so a hung host can't stall it.
    """
    ports = ports if ports is not None else SCAN_PORTS
    candidates = (
        _expand_hosts(hosts)
        if hosts is not None
        else (_expand_hosts([f"{ip}/24"]) if (ip := _local_ipv4()) else [])
    )
    if not candidates:
        raise ValueError("no hosts to scan: not on a network, or an empty host list was given")
    if len(candidates) > _SCAN_MAX_CANDIDATES:
        raise ValueError(
            f"{len(candidates)} candidate hosts exceeds the {_SCAN_MAX_CANDIDATES} cap; "
            "pass a narrower CIDR or explicit hosts"
        )
    gate = asyncio.Semaphore(concurrency)

    async def check(host: str, port: int) -> dict[str, Any] | None:
        async with gate:
            if not await _tcp_accepts(host, port, connect_timeout):
                return None
            url = f"http://{host}:{port}"
            try:
                info = await asyncio.wait_for(_identify(url), identify_timeout)
            except (TimeoutError, httpx.HTTPError):
                return None
            if info is None:
                return None
            return {
                "url": url,
                "host": host,
                "port": port,
                "kind": info["kind"],
                "version": info.get("version"),
            }

    results = await asyncio.gather(*(check(h, p) for h in candidates for p in ports))
    return [r for r in results if r is not None]


async def detect_target(base_url: str) -> dict[str, Any]:
    """What is at *base_url* (robot / fleet / dispatcher) and which MiR
    software version does it run? Cached per URL after the first success."""
    if base_url in _detected:
        return _detected[base_url]
    info = await _identify(base_url)
    if info is None:
        return {"kind": "unknown", "version": None}
    _detected[base_url] = info
    return info


async def resolved_robot_base() -> str:
    """Robot API root: the target itself, or the right dispatcher mount."""
    base = robot_base_url()
    info = await detect_target(base)
    if info["kind"] != "dispatcher":
        return base
    version = os.environ.get("AMR_VERSION") or info["latest"]
    if version not in info["versions"]:
        raise TargetResolutionError(
            f"Error: AMR_VERSION={version} is not served by {base}; "
            f"it serves: {', '.join(info['versions'])}."
        )
    return f"{base}/{version}"


async def resolved_fleet_base() -> str:
    base = fleet_base_url()
    info = await detect_target(base)
    if info["kind"] != "dispatcher":
        return base
    if not info["fleet_versions"]:
        raise TargetResolutionError(f"Error: {base} serves no fleet versions.")
    version = os.environ.get("AMR_FLEET_VERSION") or info["fleet_latest"]
    if version not in info["fleet_versions"]:
        raise TargetResolutionError(
            f"Error: AMR_FLEET_VERSION={version} is not served by {base}; "
            f"it serves: {', '.join(info['fleet_versions'])}."
        )
    return f"{base}/fleet/{version}"


async def robot_request(
    method: str,
    path: str,
    *,
    json: Any = None,
    api: bool = True,
) -> tuple[int, Any]:
    """Call the robot. ``api=True`` prefixes /api/v2.0.0; emulator-only
    surfaces (``/_emulator/*``) live at the root and pass ``api=False``."""
    prefix = ROBOT_API_PREFIX if api else ""
    base = await resolved_robot_base()
    return await _request(base, robot_headers(), method, f"{prefix}{path}", json=json)


async def fleet_request(method: str, path: str, *, json: Any = None) -> tuple[int, Any]:
    base = await resolved_fleet_base()
    return await _request(base, fleet_headers(), method, f"{FLEET_API_PREFIX}{path}", json=json)


def describe_http_error(status: int, body: Any, target: str) -> str:
    detail = ""
    if isinstance(body, dict):
        detail = str(body.get("error_human") or body.get("error_code") or "")
    if status == 401:
        return (
            f"Error: {target} rejected the credentials (401). Check AMR_USERNAME/"
            "AMR_PASSWORD (robot) or AMR_API_KEY (fleet); the emulator default "
            "for all three is 'distributor'."
        )
    if status == 404:
        return f"Error: not found (404). {detail or 'Check the id — list it first.'}"
    return f"Error: {target} answered {status}. {detail}".strip()


def describe_connection_error(exc: Exception, url: str) -> str:
    return (
        f"Error: cannot reach {url} ({type(exc).__name__}). If you meant the "
        "emulator, start one with `uv run amr-emulator` (robot) or "
        "`uv run amr-emulator --fleet-version 1.5.0` (fleet), or point "
        "AMR_ROBOT_URL/AMR_FLEET_URL at the right host."
    )
