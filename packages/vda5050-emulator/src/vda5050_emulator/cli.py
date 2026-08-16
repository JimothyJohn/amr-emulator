"""Run the emulator: ``vda5050-emulator`` and point your master control at it.

Zero-configuration path: no arguments starts an embedded MQTT broker on :1883
with one emulated robot connected to it, and prints the exact topics to use.
If a master control already has a broker, ``--broker host[:port]`` connects
the emulated robots to that broker instead and no embedded broker is started.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import os
import signal

from ._version import __version__
from .clock import SimClock
from .profiles import profile as get_profile
from .profiles import supported_versions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vda5050-emulator",
        description=(
            "Local emulator of VDA 5050 mobile robots (MQTT + JSON). With no "
            "arguments it starts an embedded MQTT broker on :1883 plus one robot."
        ),
    )
    parser.add_argument(
        "--spec",
        default="3.0.0",
        metavar="VERSION",
        help=f"VDA 5050 version to speak; one of {', '.join(supported_versions())} "
        "(default: 3.0.0)",
    )
    parser.add_argument(
        "--broker",
        default=None,
        metavar="HOST[:PORT]",
        help="connect the robots to this existing MQTT broker instead of "
        "starting the embedded one (default port 1883)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="embedded broker bind address")  # noqa: S104
    parser.add_argument("--port", type=int, default=1883, help="embedded broker port")
    parser.add_argument("--robots", type=int, default=1, metavar="N", help="number of robots")
    parser.add_argument("--manufacturer", default="amr-emulator")
    parser.add_argument(
        "--serial",
        default="vagv-{:04d}",
        metavar="PATTERN",
        help="serial number pattern; '{}' formats the robot index (default vagv-{:04d})",
    )
    parser.add_argument(
        "--interface-name",
        default=None,
        metavar="NAME",
        help="first MQTT topic level (default: 'vda5050' for 3.x, 'uagv' for 2.x)",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("VDA5050_EMULATOR_USERNAME"),
        help="MQTT username (embedded broker requires it from clients too)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("VDA5050_EMULATOR_PASSWORD"),
        help="MQTT password (env: VDA5050_EMULATOR_PASSWORD)",
    )
    parser.add_argument(
        "--time-scale",
        type=float,
        default=1.0,
        metavar="N",
        help="run simulated time Nx faster than wall time",
    )
    parser.add_argument(
        "--map-id", default="map-0", help="mapId the robots start on (default map-0)"
    )
    parser.add_argument(
        "--state-interval",
        type=float,
        default=30.0,
        metavar="SECONDS",
        help="periodic state publish interval in simulated seconds (events always publish; "
        "lower this below a master control's heartbeat timeout)",
    )
    parser.add_argument(
        "--visualization-interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="visualization publish interval in simulated seconds; 0 disables",
    )
    parser.add_argument("--version", action="version", version=f"vda5050-emulator {__version__}")
    return parser


def _parse_broker(value: str) -> tuple[str, int]:
    value = value.removeprefix("mqtt://").removeprefix("tcp://")
    host, _, port = value.partition(":")
    return host or "127.0.0.1", int(port) if port else 1883


async def _run(args: argparse.Namespace) -> int:
    from .robot import AGVConfig, VirtualAGV

    get_profile(args.spec)  # fail fast on unknown --spec
    clock = SimClock(scale=args.time_scale)

    broker = None
    if args.broker:
        host, port = _parse_broker(args.broker)
        where = f"external broker mqtt://{host}:{port}"
    else:
        from .mqtt import Broker

        broker = Broker(args.host, args.port, username=args.username, password=args.password)
        await broker.start()
        host, port = ("127.0.0.1" if args.host == "0.0.0.0" else args.host, broker.port)  # noqa: S104
        where = f"embedded broker on mqtt://{args.host}:{broker.port}"

    robots: list[VirtualAGV] = []
    for index in range(1, args.robots + 1):
        serial = (
            args.serial.format(index)
            if "{" in args.serial
            else (args.serial if args.robots == 1 else f"{args.serial}-{index}")
        )
        config = AGVConfig(
            manufacturer=args.manufacturer,
            serial_number=serial,
            version=args.spec,
            interface_name=args.interface_name,
            map_id=args.map_id,
            x=float(index - 1) * 2.0,
            visualization_interval=args.visualization_interval,
            default_state_interval=args.state_interval,
            username=args.username,
            password=args.password,
        )
        robot = VirtualAGV(config, host=host, port=port, clock=clock)
        await robot.start()
        robots.append(robot)

    print(f"vda5050-emulator: VDA 5050 {args.spec}, {where}")
    if args.time_scale != 1.0:
        print(f"time scale: {args.time_scale}x (simulated seconds per wall second)")
    for robot in robots:
        print(f"robot: {robot.topics.prefix}/{{order,instantActions,state,connection,...}}")
    example = robots[0].topics
    print("\nfive-minute check with any MQTT client:")
    print(f"  subscribe: {example.interface_name}/{example.major_version}/+/+/state")
    print(f"  publish an order to: {example.topic('order')}")
    print(f"  fault injection (JSON): {example.topic('_emulator')}")
    print('    e.g. {"emergencyStop": "MANUAL"} or {"battery": {"level": 7}}')

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop.set)
    await stop.wait()
    print("shutting down (OFFLINE + clean disconnect) ...")
    for robot in robots:
        await robot.stop()
    if broker is not None:
        await broker.stop()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
