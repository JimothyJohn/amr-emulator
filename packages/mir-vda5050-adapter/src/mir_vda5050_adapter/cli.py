"""Run the adapter: ``mir-vda5050-adapter --mir-url http://<robot> --broker <mqtt-host>``.

With no arguments it assumes a MiR (or mir-emulator) on :8080 and an MQTT
broker on :1883. Any broker works — including the vda5050-emulator's embedded
one (`vda5050-emulator --robots 0` starts broker-only).
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import os
import signal

from vda5050_emulator.profiles import supported_versions

from ._version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mir-vda5050-adapter",
        description="Expose a MiR robot (real or emulated) as a VDA 5050 robot over MQTT.",
    )
    parser.add_argument("--mir-url", default="http://127.0.0.1:8080")
    parser.add_argument("--mir-username", default=os.environ.get("MIR_USERNAME", "distributor"))
    parser.add_argument("--mir-password", default=os.environ.get("MIR_PASSWORD", "distributor"))
    parser.add_argument("--broker", default="127.0.0.1:1883", metavar="HOST[:PORT]")
    parser.add_argument(
        "--spec",
        default="2.0.0",
        help=f"VDA 5050 version to speak; one of {', '.join(supported_versions())}",
    )
    parser.add_argument("--manufacturer", default="MiR")
    parser.add_argument("--serial", default="mir-robot-1")
    parser.add_argument("--interface-name", default=None)
    parser.add_argument("--version", action="version", version=f"mir-vda5050-adapter {__version__}")
    return parser


async def _run(args: argparse.Namespace) -> int:
    from .adapter import AdapterConfig, MiRVDA5050Adapter

    host, _, port = args.broker.removeprefix("mqtt://").partition(":")
    config = AdapterConfig(
        mir_url=args.mir_url,
        mir_username=args.mir_username,
        mir_password=args.mir_password,
        manufacturer=args.manufacturer,
        serial_number=args.serial,
        version=args.spec,
        interface_name=args.interface_name,
    )
    adapter = MiRVDA5050Adapter(config, host=host or "127.0.0.1", port=int(port or 1883))
    await adapter.start()
    print(f"mir-vda5050-adapter: MiR at {args.mir_url} <-> VDA 5050 {args.spec}")
    print(f"robot topics: {adapter.topics.prefix}/{{order,instantActions,state,...}}")
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop.set)
    await stop.wait()
    await adapter.stop()
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return asyncio.run(_run(build_parser().parse_args(argv)))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
