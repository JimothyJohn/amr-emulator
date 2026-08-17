#!/usr/bin/env python3
"""External conformance run: vda5050-master vs the OTTO/InOrbit/Ekumen connector.

Closes the loop the in-repo suites cannot: both sides of every other test in
this repo share our schemas, profiles, and assumptions. Here the robot side
is the unmodified open-source VDA 5050 <-> ROS 2 connector that ships in
OTTO Motors' product (github.com/inorbit-ai/ros_amr_interop, pinned in the
Dockerfile), driven over our embedded MQTT broker by our FleetMaster.

Phases:
  1. lifecycle — dispatch a 3-waypoint order with a HARD action; expect
     COMPLETED with the connector reporting every node/action finished.
  2. horizon  — 4 waypoints released 2 at a time; expects the connector to
     accept stitched order updates; expect COMPLETED.
  3. cancel   — dispatch, wait until RUNNING, cancelOrder; expect CANCELED.

Exit code 0 only if all phases pass AND the connector never published a
message our schema validation rejects (RobotHandle.protocol_problems empty).

Usage: uv run interop/otto-vda5050/run_interop.py [--keep] [--skip-build]
Requires Docker. First build downloads the ROS base image (~1 GB).
"""

from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

from vda5050_emulator import Broker
from vda5050_master import FleetMaster, Mission, MissionController, Waypoint, action
from vda5050_master.controller import MissionStatus

HERE = Path(__file__).parent
IMAGE = "amr-otto-vda5050-interop"
SERIAL = "OTTO_1"


def sh(*cmd: str, capture: bool = False) -> str:
    result = subprocess.run(cmd, check=True, text=True, capture_output=capture)
    return result.stdout.strip() if capture else ""


async def wait_for(predicate, *, timeout: float, interval: float = 0.2, what: str = ""):
    deadline = asyncio.get_running_loop().time() + timeout
    while not predicate():
        if asyncio.get_running_loop().time() > deadline:
            raise TimeoutError(f"timed out waiting for {what}")
        await asyncio.sleep(interval)


async def run(keep: bool, skip_build: bool) -> int:
    if not skip_build:
        print(f"building {IMAGE} (connector pinned in Dockerfile)...")
        sh("docker", "build", "-t", IMAGE, str(HERE))

    broker = Broker(host="0.0.0.0", port=0)
    await broker.start()
    print(f"embedded broker listening on 0.0.0.0:{broker.port}")

    container = sh(
        "docker",
        "run",
        "-d",
        "--rm",
        "-e",
        "MQTT_HOST=host.docker.internal",
        "-e",
        f"MQTT_PORT={broker.port}",
        IMAGE,
        capture=True,
    )
    print(f"connector container {container[:12]} started")

    failures: list[str] = []
    master = FleetMaster("127.0.0.1", broker.port, version="2.0.0")
    try:
        await master.connect()
        handle = (await master.wait_for_robots(1, timeout=120))[0]
        print(f"discovered {handle.manufacturer}/{handle.serial_number} ONLINE")

        # The bridge reports ONLINE while the controller may still be blocked
        # waiting on the adapter, and an order published in that window is
        # silently dropped on the ROS side. The controller publishes state
        # only once fully up — gate dispatch on the first state message.
        await handle.next_state(lambda _: True, timeout=60, past=False)
        print("controller is publishing state; dispatching")

        control = MissionController(master)

        # Phase 1: full lifecycle with a HARD action at the middle stop.
        lifecycle = Mission(
            [
                Waypoint(x=0.0, y=0.0, map_id="map", theta=0.0),
                Waypoint(
                    x=5.0,
                    y=0.0,
                    map_id="map",
                    theta=0.0,
                    actions=(action("pick", blocking_type="HARD"),),
                ),
                Waypoint(x=5.0, y=4.0, map_id="map", theta=0.0),
            ],
            name="lifecycle",
        )
        run1 = control.submit(lifecycle, timeout=60.0)
        status = await run1.wait(timeout=90)
        print(f"phase 1 lifecycle: {status.name} {run1.failure}")
        if status is not MissionStatus.COMPLETED:
            failures.append(f"lifecycle ended {status.name} ({run1.failure})")

        # Phase 2: base/horizon release — exercises stitched order updates.
        horizon = Mission(
            [
                Waypoint(x=5.0, y=4.0, map_id="map", theta=0.0),
                Waypoint(x=0.0, y=4.0, map_id="map", theta=0.0),
                Waypoint(x=0.0, y=8.0, map_id="map", theta=0.0),
                Waypoint(x=4.0, y=8.0, map_id="map", theta=0.0),
            ],
            name="horizon",
        )
        run2 = control.submit(horizon, release=2, timeout=60.0)
        status = await run2.wait(timeout=120)
        print(f"phase 2 horizon: {status.name} {run2.failure}")
        if status is not MissionStatus.COMPLETED:
            failures.append(f"horizon ended {status.name} ({run2.failure})")

        # Phase 3: cancelOrder — documented upstream divergence probe.
        # The official 2.0.0 instantActions schema REQUIRES actionName, but
        # the connector kwarg-splats the JSON into ROS messages, so its MQTT
        # thread dies with AssertionError('action_name') on ANY schema-valid
        # 2.0.0 instant action. This probe PASSES while that bug reproduces
        # (cancelOrder unacknowledged) and FAILS if upstream fixes it, so the
        # divergence note in the README gets retired instead of rotting.
        long_haul = Mission(
            [Waypoint(x=float(i), y=12.0, map_id="map", theta=0.0) for i in range(30)],
            name="cancel-me",
        )
        run3 = control.submit(long_haul, timeout=60.0)
        await wait_for(
            lambda: run3.status is MissionStatus.RUNNING or run3.done,
            timeout=60,
            what="cancel-me to start RUNNING",
        )
        try:
            await handle.cancel_order(timeout=10.0)
        except TimeoutError:
            print(
                "phase 3 cancel: EXPECTED-DIVERGENCE reproduced — schema-valid "
                "cancelOrder (actionName) unacknowledged, connector bridge dead"
            )
        else:
            failures.append(
                "cancelOrder was acknowledged: upstream fixed the actionName "
                "bug — retire the divergence note and restore the CANCELED assertion"
            )
        # The bridge thread is dead now; the run can never settle. shutdown()
        # cancels the worker outright rather than waiting out its timeout.
        await control.shutdown()

        if handle.protocol_problems:
            failures.append(
                f"connector published {len(handle.protocol_problems)} message(s) "
                f"failing official-schema validation: {handle.protocol_problems}"
            )
        else:
            print("schema validation: every connector message passed")
    finally:
        await master.disconnect()
        if keep:
            print(f"--keep: container {container[:12]} left running")
        else:
            if failures:
                subprocess.run(["docker", "logs", "--tail", "400", container], text=True)
            subprocess.run(["docker", "rm", "-f", container], capture_output=True)
        await broker.stop()

    if failures:
        print("\nFAIL:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "\nPASS: full order lifecycle and stitched updates against the "
        "unmodified OTTO/InOrbit/Ekumen connector with zero validation "
        "failures on either side; cancelOrder divergence reproduced as "
        "documented (see README)."
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="leave the container running")
    parser.add_argument("--skip-build", action="store_true", help="reuse the existing image")
    args = parser.parse_args()
    sys.exit(asyncio.run(run(keep=args.keep, skip_build=args.skip_build)))


if __name__ == "__main__":
    main()
