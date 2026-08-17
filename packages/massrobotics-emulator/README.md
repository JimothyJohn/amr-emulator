# massrobotics-emulator

Emulator for the [MassRobotics AMR Interoperability Standard](https://github.com/MassRobotics-AMR/AMR_Interop_Standard)
— the open interop layer Vecna Robotics co-developed and certifies its
fleet against (APT autonomous pallet truck, ATG tugger, AFL counterbalanced
forklift, CPJ cobot pallet jack). Both roles ship in this package:

- **`MassRoboticsAMR`** (robot / sender): a WebSocket client that delivers
  one `identityReport` and streams `statusReports` while a simple movement
  model drives position, heading, velocity, battery, and predicted
  path/destinations. Vecna presets via `vecna_config("APT" | "ATG" | "AFL"
  | "CPJ")`; any identity via `AMRConfig`.
- **`InteropReceiver`** (fleet side): a WebSocket server that validates
  every incoming message against the official schema and keeps a live
  per-robot registry — identity, status history, connection state, and
  recorded validation problems (never silently dropped).

The transport is a hand-rolled stdlib RFC 6455 implementation (`ws.py`) in
the same spirit as the VDA 5050 package's embedded MQTT stack: zero runtime
network dependencies, strict about protocol edges (masking, fragmentation,
control frames, close codes).

## Five-minute story

```sh
uv run massrobotics-emulator receiver --port 3000
uv run massrobotics-emulator robot --receiver ws://127.0.0.1:3000 --model APT --count 2 --patrol
```

Or in code:

```python
import asyncio
from massrobotics_emulator import InteropReceiver, MassRoboticsAMR, vecna_config


async def main():
    receiver = InteropReceiver()
    await receiver.start()
    robot = MassRoboticsAMR(vecna_config("APT"))
    await robot.start(receiver.uri)
    (record,) = await receiver.wait_for_robots(1)
    robot.navigate_to(25.0, 10.0)
    print(await receiver.next_status(record.uuid, lambda s: s["operationalState"] == "navigating"))
    await robot.stop()
    await receiver.stop()


asyncio.run(main())
```

## The oracle

`schemas/AMR_Interop_Standard.json` is vendored byte-for-byte from the
official repository (commit and sha256 in `schemas/registry.json`). Every
outgoing message is validated against it and **raises** on violation;
every incoming message is validated and recorded. Upstream quirks found
while vendoring — including that the standard's own example messages fail
its schema (uppercase UUIDs vs lowercase-only patterns) — are documented
in the registry's `notes`.

Tests: `uv run pytest packages/massrobotics-emulator` — schema quirks,
RFC 6455 conformance with adversarial raw-byte peers, and full
sender↔receiver loops on simulated time.
