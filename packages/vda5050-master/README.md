# vda5050-master

Programmable VDA 5050 master control: the fleet-manager half of the
protocol, as a Python library. Point it at an MQTT broker and it discovers
every robot (no per-robot configuration — wildcard subscriptions over the
`interfaceName/majorVersion/+/+/…` topic space), then lets you dispatch
missions and track their whole lifecycle. There is deliberately no UI yet;
this package is everything a UI would hang off.

```python
import asyncio
from vda5050_master import FleetMaster, Mission, MissionController, Waypoint, action


async def main():
    async with FleetMaster("127.0.0.1", 1883, version="3.0.0") as fleet:
        await fleet.wait_for_robots(1)
        control = MissionController(fleet)
        mission = Mission(
            [
                Waypoint(x=0.0, y=0.0),
                Waypoint(x=5.0, y=0.0, actions=(action("pick", blocking_type="HARD"),)),
                Waypoint(x=5.0, y=4.0, actions=(action("drop", blocking_type="HARD"),)),
            ],
            name="shuttle",
        )
        run = control.submit(mission, release=2)  # 2-waypoint base, rest as horizon
        print(await run.wait())  # MissionStatus.COMPLETED
        await control.shutdown()


asyncio.run(main())
```

The three layers (use as much or as little as you need):

- **`FleetMaster` / `RobotHandle`** — discovery, connection tracking via the
  `connection` topic (last-will-backed), per-robot schema-validated
  publishing with correct `headerId` sequencing, and awaitable predicates
  over `state`/`connection`/`factsheet`/`visualization`. Outgoing messages
  that violate the official schemas raise instead of publishing; incoming
  violations are recorded on `RobotHandle.protocol_problems`, never dropped.
- **`Mission` / `Waypoint`** — routes with per-stop actions, compiled to
  orders obeying every structural rule of the acceptance process
  (sequenceId interleaving, contiguous released prefix, decision-point
  stitching for updates), for any supported version (2.0.0 / 2.1.0 / 3.0.0
  wire differences handled by the shared profiles).
- **`MissionController` / `MissionRun`** — per-robot FIFO queues,
  least-busy assignment, base/horizon release (`release=<n>`), rejection
  detection via `errorReferences` (2.x-safe: five rejections share one wire
  errorType there), retries with fresh orderIds, cancellation
  (`cancelOrder`), RETRIABLE resolution via `skipRetry`, and
  offline-mid-mission failure. `run.wait()` resolves to
  `COMPLETED | FAILED | CANCELED` with the robot's errors captured on the
  run.

Tests exercise all of it against this repo's `vda5050-emulator` robots over
the real embedded broker — no mocks. `uv run pytest packages/vda5050-master`.
