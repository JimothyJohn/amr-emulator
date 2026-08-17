"""Command-line entry points: emulated Vecna-class robots, or a receiver.

Five-minute story, mirroring the VDA 5050 package: run a receiver (or point
at a real one), start a robot fleet against it, watch schema-clean interop
reports flow.

    massrobotics-emulator receiver --port 3000
    massrobotics-emulator robot --receiver ws://127.0.0.1:3000 --model APT --count 2
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import itertools
import json

from ._version import __version__
from .receiver import InteropReceiver
from .robot import VECNA_MODELS, MassRoboticsAMR, vecna_config

PATROL = [(0.0, 0.0), (25.0, 0.0), (25.0, 15.0), (0.0, 15.0)]


async def _run_robots(args: argparse.Namespace) -> None:
    robots = []
    for n in range(args.count):
        config = vecna_config(
            args.model,
            serial_number=f"{args.model}-{n + 1:04d}",
            status_interval=args.interval,
            x=float(5 * n),
        )
        robot = MassRoboticsAMR(config)
        await robot.start(args.receiver)
        robots.append(robot)
        print(f"{config.robot_serial_number} ({config.uuid}) -> {args.receiver}")
    try:
        if not args.patrol:
            await asyncio.Event().wait()  # stream idle statuses forever
        for corner in itertools.cycle(PATROL):
            for robot in robots:
                robot.navigate_to(*corner)
            for robot in robots:
                await robot.wait_for_arrival(timeout=120)
    finally:
        for robot in robots:
            await robot.stop()


async def _run_receiver(args: argparse.Namespace) -> None:
    receiver = InteropReceiver(host=args.host, port=args.port)
    await receiver.start()
    print(f"MassRobotics AMR Interop receiver on ws://{args.host}:{receiver.port}")
    known: set[str] = set()
    reported: dict[str, int] = {}
    try:
        while True:
            await asyncio.sleep(1)
            for uuid, record in receiver.robots.items():
                if uuid not in known and record.identity is not None:
                    known.add(uuid)
                    identity = record.identity
                    print(
                        f"+ {identity['manufacturerName']} {identity['robotModel']} "
                        f"sn={identity['robotSerialNumber']} uuid={uuid}"
                    )
                for kind, problems in record.problems[reported.get(uuid, 0) :]:
                    print(f"! {uuid} invalid {kind}: {problems}")
                reported[uuid] = len(record.problems)
                if args.verbose and record.latest:
                    print(json.dumps(record.latest))
    finally:
        await receiver.stop()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="massrobotics-emulator",
        description="MassRobotics AMR Interop Standard emulator (Vecna-class fleet)",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    robot = sub.add_parser("robot", help="emulate robots reporting to a receiver")
    robot.add_argument("--receiver", default="ws://127.0.0.1:3000", help="receiver ws:// URI")
    robot.add_argument("--model", default="APT", choices=sorted(VECNA_MODELS))
    robot.add_argument("--count", type=int, default=1)
    robot.add_argument("--interval", type=float, default=1.0, help="statusReport period, seconds")
    robot.add_argument(
        "--patrol", action="store_true", help="drive a patrol loop instead of idling"
    )
    robot.set_defaults(run=_run_robots)

    receiver = sub.add_parser("receiver", help="run a validating interop receiver")
    receiver.add_argument("--host", default="127.0.0.1")
    receiver.add_argument("--port", type=int, default=3000)
    receiver.add_argument("--verbose", action="store_true", help="print each statusReport")
    receiver.set_defaults(run=_run_receiver)

    args = parser.parse_args(argv)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(args.run(args))


if __name__ == "__main__":
    main()
