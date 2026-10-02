"""Typed clients for the MiR robot REST API and Fleet Integration API.

``amr_client.robot`` and ``amr_client.fleet`` are generated verbatim from the
official specs (see _provenance for exact versions and hashes); this module
adds the two constructors that wire in MiR's authentication schemes.
"""

from __future__ import annotations

from typing import Any

from amr_client import _provenance as provenance
from amr_client.auth import DEFAULT_PASSWORD, DEFAULT_USERNAME, robot_token
from amr_client.discovery import (
    DiscoveryError,
    ServerInfo,
    _warn_if_generation_gap,
    detect_server,
    detect_server_async,
)
from amr_client.fleet.client import AuthenticatedClient as _FleetClient
from amr_client.robot.client import AuthenticatedClient as _RobotClient
from amr_client.scan import (
    DiscoveredServer,
    scan_network,
    scan_network_async,
)

DEFAULT_API_KEY = "distributor"  # the emulator's default; real fleets issue keys


def robot_client(
    base_url: str,
    *,
    username: str = DEFAULT_USERNAME,
    password: str = DEFAULT_PASSWORD,
    **httpx_kwargs: Any,
) -> _RobotClient:
    """A client for one robot: *base_url* is the robot's root (no /api/v2.0.0)."""
    return _RobotClient(
        base_url=base_url.rstrip("/") + "/api/v2.0.0",
        token=robot_token(username, password),
        prefix="Basic",
        httpx_args=httpx_kwargs,
    )


def fleet_client(
    base_url: str, *, api_key: str = DEFAULT_API_KEY, **httpx_kwargs: Any
) -> _FleetClient:
    """A client for MiR Fleet Enterprise: *base_url* is the fleet root."""
    return _FleetClient(
        base_url=base_url.rstrip("/"),
        token=api_key,
        prefix="",
        auth_header_name="x-api-key",
        httpx_args=httpx_kwargs,
    )


def client_for(
    info: ServerInfo,
    *,
    version: str | None = None,
    username: str = DEFAULT_USERNAME,
    password: str = DEFAULT_PASSWORD,
    api_key: str = DEFAULT_API_KEY,
    **httpx_kwargs: Any,
) -> _RobotClient | _FleetClient:
    """Build the right client for an already-detected target.

    *version* only selects among a dispatcher's mounts; a single robot or
    fleet runs what it runs, so a conflicting request is an error, not a
    silent downgrade.
    """
    if info.kind == "dispatcher":
        if version is None:
            chosen = info.latest or info.versions[0]
        elif version in info.versions or version in info.fleet_versions:
            chosen = version
        else:
            served = ", ".join((*info.versions, *info.fleet_versions))
            raise DiscoveryError(f"{info.base_url} does not serve {version}; it serves: {served}")
        if chosen in info.fleet_versions:
            return fleet_client(f"{info.base_url}/fleet/{chosen}", api_key=api_key, **httpx_kwargs)
        return robot_client(
            f"{info.base_url}/{chosen}", username=username, password=password, **httpx_kwargs
        )
    if version is not None and info.version is not None and version != info.version:
        raise DiscoveryError(
            f"{info.base_url} is a {info.kind} running {info.version}; a client cannot "
            f"switch it to {version}"
        )
    _warn_if_generation_gap(info)
    if info.kind == "fleet":
        return fleet_client(info.base_url, api_key=api_key, **httpx_kwargs)
    return robot_client(info.base_url, username=username, password=password, **httpx_kwargs)


def connect(
    base_url: str,
    *,
    version: str | None = None,
    username: str = DEFAULT_USERNAME,
    password: str = DEFAULT_PASSWORD,
    api_key: str = DEFAULT_API_KEY,
    timeout: float = 5.0,
    **httpx_kwargs: Any,
) -> _RobotClient | _FleetClient:
    """Detect what lives at *base_url* and return a ready client for it.

    Works against a single robot, a MiR Fleet, or the multi-version demo
    dispatcher — no need to know (or install) the matching version first.
    """
    info = detect_server(base_url, api_key=api_key, timeout=timeout, **httpx_kwargs)
    return client_for(
        info,
        version=version,
        username=username,
        password=password,
        api_key=api_key,
        **httpx_kwargs,
    )


__all__ = [
    "DEFAULT_API_KEY",
    "DEFAULT_PASSWORD",
    "DEFAULT_USERNAME",
    "DiscoveredServer",
    "DiscoveryError",
    "ServerInfo",
    "client_for",
    "connect",
    "detect_server",
    "detect_server_async",
    "fleet_client",
    "provenance",
    "robot_client",
    "robot_token",
    "scan_network",
    "scan_network_async",
]
