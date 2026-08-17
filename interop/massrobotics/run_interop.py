#!/usr/bin/env python3
"""External conformance run: massrobotics-emulator vs the official receiver.

Self-validation is circular: the emulator's sender and receiver share this
repo's schema handling. Here the robot fleet (all four Vecna models) reports
to the standard's own reference receiver (Node + Ajv, unmodified, pinned in
the Dockerfile), and a witness connection on the receiver's /ui endpoint
collects its {message, isValid, errors} verdict for every message.

PASS requires:
  - the official receiver judges every identityReport and statusReport we
    send (idle, navigating with path/destinations, erroring, charging) valid;
  - the witness channel is proven live by a deliberately-invalid probe
    message that the receiver must judge invalid.

Usage: uv run interop/massrobotics/run_interop.py [--keep] [--skip-build]
Requires Docker.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import subprocess
import sys
from pathlib import Path

from massrobotics_emulator import MassRoboticsAMR, vecna_config
from massrobotics_emulator import ws as ws_module

HERE = Path(__file__).parent
IMAGE = "amr-massrobotics-interop"
MODELS = ("APT", "ATG", "AFL", "CPJ")
STATUSES_PER_ROBOT = 8


def sh(*cmd: str, capture: bool = False) -> str:
    result = subprocess.run(list(cmd), check=True, text=True, capture_output=capture)
    return result.stdout.strip() if capture else ""


async def run(keep: bool, skip_build: bool) -> int:
    if not skip_build:
        print(f"building {IMAGE} (official receiver pinned in Dockerfile)...")
        sh("docker", "build", "-t", IMAGE, str(HERE))

    container = sh("docker", "run", "-d", "--rm", "-p", "127.0.0.1:0:3000", IMAGE, capture=True)
    port = sh(
        "docker",
        "inspect",
        "-f",
        '{{(index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort}}',
        container,
        capture=True,
    )
    print(f"official receiver container {container[:12]} on 127.0.0.1:{port}")

    failures: list[str] = []
    verdicts: list[dict] = []
    robots: list[MassRoboticsAMR] = []
    witness = None
    collector = None
    try:
        # The Node server needs a moment to come up.
        witness = await _connect_with_retry(f"ws://127.0.0.1:{port}/ui", attempts=30)

        async def collect() -> None:
            while True:
                verdicts.append(json.loads(await witness.receive_text()))

        collector = asyncio.create_task(collect())

        for n, model in enumerate(MODELS):
            robot = MassRoboticsAMR(vecna_config(model, status_interval=0.2, x=float(10 * n)))
            await robot.start(f"ws://127.0.0.1:{port}")
            robots.append(robot)

        # Exercise the interesting status shapes on each robot.
        for n, robot in enumerate(robots):
            robot.navigate_to(50.0, float(5 * n))
        robots[0].set_error("E-STOP")
        robots[1].set_charging(True)
        await asyncio.sleep(STATUSES_PER_ROBOT * 0.2)
        robots[0].clear_errors()
        for robot in robots:
            await robot.stop()

        # Prove the witness channel actually detects invalidity.
        probe = await ws_module.connect(f"ws://127.0.0.1:{port}")
        await probe.send_text(json.dumps({"uuid": "not-even-a-uuid"}))
        await probe.close()

        await asyncio.sleep(1.0)  # let the last verdicts arrive
        collector.cancel()

        ours = [
            v
            for v in verdicts
            if isinstance(v.get("message"), dict) and v["message"].get("uuid") != "not-even-a-uuid"
        ]
        probes = [
            v
            for v in verdicts
            if isinstance(v.get("message"), dict) and v["message"].get("uuid") == "not-even-a-uuid"
        ]

        invalid = [v for v in ours if not v.get("isValid")]
        identities = [v for v in ours if "manufacturerName" in v["message"]]
        navigating = [v for v in ours if v["message"].get("operationalState") == "navigating"]
        print(
            f"official receiver judged {len(ours)} emulator messages: "
            f"{len(identities)} identities, {len(ours) - len(identities)} statuses "
            f"({len(navigating)} navigating), {len(invalid)} invalid"
        )
        if len(identities) < len(MODELS):
            failures.append(f"expected {len(MODELS)} identityReports, saw {len(identities)}")
        if len(ours) < len(MODELS) * STATUSES_PER_ROBOT // 2:
            failures.append(f"too few messages witnessed ({len(ours)}) — stream broken?")
        if not navigating:
            failures.append("no navigating status (path/destinations) was witnessed")
        for verdict in invalid:
            failures.append(
                f"official receiver rejected our message: {verdict.get('errors')} "
                f"for {json.dumps(verdict['message'])[:160]}"
            )
        if not probes or probes[0].get("isValid"):
            failures.append(
                "witness sanity probe failed: the deliberately-invalid message "
                "was not judged invalid — verdicts cannot be trusted"
            )
    finally:
        for robot in robots:
            with contextlib.suppress(Exception):
                await robot.stop()
        if collector is not None:
            collector.cancel()
        if witness is not None:
            await witness.close()
        if keep:
            print(f"--keep: container {container[:12]} left running")
        else:
            if failures:
                subprocess.run(["docker", "logs", "--tail", "100", container], text=True)
            subprocess.run(["docker", "rm", "-f", container], capture_output=True)

    if failures:
        print("\nFAIL:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "\nPASS: the official MassRobotics reference receiver accepted every "
        "message from all four Vecna-model emulated robots, and the witness "
        "channel demonstrably detects invalid traffic."
    )
    return 0


async def _connect_with_retry(uri: str, *, attempts: int) -> ws_module.WebSocket:
    for attempt in range(attempts):
        try:
            return await ws_module.connect(uri)
        except (ConnectionError, OSError, ws_module.WSError):
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(1.0)
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="leave the container running")
    parser.add_argument("--skip-build", action="store_true", help="reuse the existing image")
    args = parser.parse_args()
    sys.exit(asyncio.run(run(keep=args.keep, skip_build=args.skip_build)))


if __name__ == "__main__":
    main()
