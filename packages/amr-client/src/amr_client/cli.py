"""``amr-discover`` — find MiR robots and fleets on the network.

amr-discover                 # scan the local /24 on ports 80, 8080
amr-discover 192.168.12.0/24 # a specific subnet
amr-discover mir.local:8080  # a specific host[:port]
amr-discover --json          # machine-readable output
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from amr_client.scan import DEFAULT_SCAN_PORTS, DiscoveredServer, scan_network


def _split_host_port(target: str, default_ports: Sequence[int]) -> tuple[str, list[int]]:
    # A CIDR block keeps the default port list; host:port pins one port.
    if "/" in target or ":" not in target:
        return target, list(default_ports)
    host, _, port = target.rpartition(":")
    return host, [int(port)]


def _render(servers: list[DiscoveredServer]) -> str:
    if not servers:
        return "No MiR robots or fleets found."
    lines = [f"Found {len(servers)} MiR target(s):"]
    for server in servers:
        version = server.info.version or "version not reported"
        lines.append(f"  {server.url}  [{server.info.kind}] {version}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="amr-discover",
        description="Scan the network for MiR robots, fleets, and emulators.",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="host, host:port, or CIDR to scan (default: the local /24)",
    )
    parser.add_argument(
        "--ports",
        default=",".join(str(p) for p in DEFAULT_SCAN_PORTS),
        help=f"comma-separated ports (default: {','.join(str(p) for p in DEFAULT_SCAN_PORTS)})",
    )
    parser.add_argument("--api-key", default="distributor", help="fleet x-api-key for probing")
    parser.add_argument("--timeout", type=float, default=4.0, help="per-host identify timeout (s)")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    default_ports = [int(p) for p in args.ports.split(",") if p.strip()]
    try:
        if args.targets:
            servers: list[DiscoveredServer] = []
            seen = set()
            for target in args.targets:
                host_spec, ports = _split_host_port(target, default_ports)
                for server in scan_network(
                    [host_spec], ports=ports, api_key=args.api_key, identify_timeout=args.timeout
                ):
                    if server.url not in seen:
                        seen.add(server.url)
                        servers.append(server)
        else:
            servers = scan_network(
                ports=default_ports, api_key=args.api_key, identify_timeout=args.timeout
            )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "url": s.url,
                        "host": s.host,
                        "port": s.port,
                        "kind": s.info.kind,
                        "version": s.info.version,
                    }
                    for s in servers
                ],
                indent=2,
            )
        )
    else:
        print(_render(servers))
    return 0 if servers else 1


if __name__ == "__main__":
    raise SystemExit(main())
