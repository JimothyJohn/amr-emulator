"""Find MiR robots on the network without knowing an IP.

``scan_network()`` sweeps a set of candidate hosts (default: the machine's
own /24) on the ports MiR gear listens on — 80 on real robots, 8080 for
this repo's emulator — with a cheap TCP connect first, then runs the
:mod:`amr_client.discovery` handshake on anything that accepts. Only
targets that positively identify as a MiR robot, fleet, or multi-version
dispatcher are returned; web servers, printers, and other LAN noise are
silently skipped.

Every network touch is bounded: TCP connects and the identification pass
each run under a hard deadline, so a host that accepts and then hangs (or
streams forever) cannot stall the sweep. The whole scan is unauthenticated
reads — safe to run on a shop-floor network.
"""

from __future__ import annotations

import asyncio
import contextlib
import ipaddress
import socket
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from amr_client.discovery import DiscoveryError, ServerInfo, detect_server_async

DEFAULT_SCAN_PORTS: tuple[int, ...] = (80, 8080)
MAX_CANDIDATES = 1024  # one /22 — beyond that, be explicit about what you scan
DEFAULT_CONNECT_TIMEOUT_S = 0.5
DEFAULT_IDENTIFY_TIMEOUT_S = 4.0
DEFAULT_CONCURRENCY = 128


@dataclass(frozen=True)
class DiscoveredServer:
    """One MiR target found by a network sweep."""

    host: str
    port: int
    url: str  # ready for connect()/robot_client()/fleet_client()
    info: ServerInfo


def local_ipv4() -> str | None:
    """The primary interface's IPv4, or None when offline.

    A UDP connect() chooses a route without sending a packet (the address
    is TEST-NET-1, never routable), so this works with no traffic at all.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 9))
            return str(probe.getsockname()[0])
    except OSError:
        return None


def expand_hosts(spec: Iterable[str]) -> list[str]:
    """Hostnames pass through; CIDR blocks expand to their usable hosts."""
    hosts: list[str] = []
    for item in spec:
        if "/" in item:
            network = ipaddress.ip_network(item, strict=False)
            hosts.extend(str(address) for address in network.hosts())
        else:
            hosts.append(item)
    # de-dup, order preserved: first mention wins
    return list(dict.fromkeys(hosts))


def default_candidates() -> list[str]:
    """The local /24 — every address this machine most likely shares a
    switch with. Empty when no interface is up."""
    ip = local_ipv4()
    if ip is None:
        return []
    return expand_hosts([f"{ip}/24"])


async def _tcp_accepts(host: str, port: int, timeout: float) -> bool:
    try:
        _reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
    except (TimeoutError, OSError):
        return False
    writer.close()
    with contextlib.suppress(Exception):
        await writer.wait_closed()
    return True


async def scan_network_async(
    hosts: Iterable[str] | None = None,
    *,
    ports: Sequence[int] = DEFAULT_SCAN_PORTS,
    api_key: str = "distributor",
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT_S,
    identify_timeout: float = DEFAULT_IDENTIFY_TIMEOUT_S,
    concurrency: int = DEFAULT_CONCURRENCY,
    **httpx_kwargs: Any,
) -> list[DiscoveredServer]:
    """Sweep every *hosts* x *ports* pair and return the targets that are MiR.

    *hosts* accepts plain hostnames/IPs and CIDR blocks; None scans the
    local /24. Results come back ordered by host then port. Raises
    ValueError when the candidate set is empty or implausibly large —
    scanning more than a /22 must be a deliberate, explicit act.
    """
    candidates = expand_hosts(hosts) if hosts is not None else default_candidates()
    if not candidates:
        raise ValueError("no hosts to scan: not on a network, or an empty host list was given")
    if len(candidates) > MAX_CANDIDATES:
        raise ValueError(
            f"{len(candidates)} candidate hosts exceeds the {MAX_CANDIDATES} cap; "
            "pass a narrower CIDR or an explicit host list"
        )
    gate = asyncio.Semaphore(concurrency)

    async def check(host: str, port: int) -> DiscoveredServer | None:
        async with gate:
            if not await _tcp_accepts(host, port, connect_timeout):
                return None
            url = f"http://{host}:{port}"
            try:
                # Outer deadline is the guarantee: a target that accepts and
                # then stalls (or streams forever) is cut off here.
                info = await asyncio.wait_for(
                    detect_server_async(
                        url,
                        api_key=api_key,
                        timeout=min(identify_timeout, 2.0),
                        **httpx_kwargs,
                    ),
                    identify_timeout,
                )
            except (TimeoutError, DiscoveryError):
                return None
            return DiscoveredServer(host=host, port=port, url=url, info=info)

    found = await asyncio.gather(*(check(h, p) for h in candidates for p in ports))
    return [server for server in found if server is not None]


def scan_network(
    hosts: Iterable[str] | None = None,
    *,
    ports: Sequence[int] = DEFAULT_SCAN_PORTS,
    api_key: str = "distributor",
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT_S,
    identify_timeout: float = DEFAULT_IDENTIFY_TIMEOUT_S,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> list[DiscoveredServer]:
    """Sync twin of :func:`scan_network_async` (same sweep, same result)."""
    return asyncio.run(
        scan_network_async(
            hosts,
            ports=ports,
            api_key=api_key,
            connect_timeout=connect_timeout,
            identify_timeout=identify_timeout,
            concurrency=concurrency,
        )
    )
