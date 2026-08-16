"""Run the ARCL emulator: ``arcl-emulator`` and telnet to it."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import signal

from ._version import __version__
from .protocol import ArclServer
from .server import DEFAULT_PASSWORD, DEFAULT_PORT, Sim


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arcl-emulator",
        description=(
            "Emulator of the Omron ARCL telnet interface (LD/HD AMRs and the "
            "Fleet Manager queuing surface). Zero-config: starts one virtual "
            "AMR with a default map."
        ),
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help="ARCL login password (a real ARCL server refuses to open without one)",
    )
    parser.add_argument("--robot-name", default="Sim_LD90")
    parser.add_argument(
        "--time-scale", type=float, default=1.0, metavar="N", help="simulated time speed-up"
    )
    parser.add_argument("--version", action="version", version=f"arcl-emulator {__version__}")
    return parser


async def _run(args: argparse.Namespace) -> int:
    sim = Sim(robot_name=args.robot_name, time_scale=args.time_scale)
    server = ArclServer(host=args.host, port=args.port, password=args.password, sim=sim)
    await server.start()
    print(f"arcl-emulator: ARCL server on {args.host}:{server.port} (robot {args.robot_name})")
    if args.password == DEFAULT_PASSWORD:
        print(f"login password: {DEFAULT_PASSWORD} (factory default)")
    else:
        print("login password: <set via --password>")
    print("\nfive-minute check:")
    print(f"  telnet {args.host} {server.port}   (or: nc {args.host} {server.port})")
    print("  <password>  ->  queuepickup Goal1  ->  watch QueueUpdate lines")
    print("  status / onelinestatus / getgoals / queueshow")
    print("  fault injection (NON-STANDARD): emulator battery 7 | emulator estop on")
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop.set)
    await stop.wait()
    await server.stop()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
