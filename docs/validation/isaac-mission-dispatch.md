# External validation: NVIDIA Isaac Mission Dispatch

Date: 2026-08-16 · emulator branch `feat/vda5050-emulator` · Mission Dispatch `4.3.0`
([nvidia-isaac/isaac_mission_dispatch](https://github.com/nvidia-isaac/isaac_mission_dispatch))

Self-validation against vendored schemas is circular — this run closes the
loop against an independent implementation of the master-control role.
NVIDIA's Isaac Mission Dispatch (paho-mqtt client, pydantic models, its own
reading of VDA 5050) connected to the **emulator's embedded MQTT broker**,
registered the emulated robot, dispatched a two-node route mission, and
tracked it to completion.

## Setup

- `uv run vda5050-emulator --port 1884 --spec 2.1.0 --manufacturer RobotCompany --serial carter01 --map-id "" --state-interval 5`
  (MD's default topic prefix is `uagv/v2/RobotCompany`; its waypoints carry `map_id: ""`.)
- Mission Dispatch 4.3.0 + mission database + postgres via docker compose
  (bridge network; `mission-dispatch --mqtt_host host.docker.internal --mqtt_port 1884 --mqtt_transport tcp`
  pointed at the emulator's broker — no mosquitto anywhere in the stack).
- Robot registered via `POST /robot {"name": "carter01", "heartbeat_timeout": 60}`;
  mission submitted via `POST /mission` (route nodes `goto_pickup`, `goto_dropoff`).

## What was validated

| Interop surface | Result |
|---|---|
| MD's paho client against the emulator's hand-rolled MQTT 3.1.1 broker | connects, subscribes, retained factsheet/connection delivered |
| Robot presence (`online`) from state heartbeats | `online: true`, drops to offline on heartbeat timeout |
| Battery telemetry from `batteryState.batteryCharge` | MD shows live percentage |
| Order acceptance + execution (3-node route, then 2-node route) | traversed, `lastNodeId`/`lastNodeSequenceId` tracked by MD |
| Sequential order chaining (mission node 2 dispatched after node 1 completes) | works |
| Pose tracking from `agvPosition` | MD shows the moving pose, final (0.00, 2.00) |
| `factsheetRequest` instant action | answered; `FINISHED` reported; MD stops re-sending |
| Mission state machine | `PENDING → RUNNING → COMPLETED`, robot `ON_TASK → IDLE` |

MD log: `Mission state: RUNNING -> COMPLETED ... Mission duration: 0:00:06.179439`.

## Transcript

```
t+  0.03s [MD api ] robot carter01 online=True battery=100.0% pose=(0.00,0.00)
t+  0.04s [MD api ] mission yegqune6dje55lhtgk4guvqjlm submitted (2 route nodes, 3 waypoints total)
t+  0.04s [MD api ] mission PENDING nodes={'goto_pickup': 'PENDING', 'goto_dropoff': 'PENDING'}
t+  0.05s [MD>robot] order yegqune6dje55lhtgk4guvqjlm-n0 (update 0): 3 nodes ['yegqune6dje55lhtgk4guvqjlm-n0-s0', 'yegqune6dje55lhtgk4guvqjlm-n0-s2', 'yegqune6dje55lhtgk4guvqjlm-n0-s4']
t+  0.06s [robot>MD] state: lastNodeId='yegqune6dje55lhtgk4guvqjlm-n0-s0' seq=0 driving=True pos=(0.00,0.00) battery=99.9% errors=[]
t+  1.06s [MD api ] mission RUNNING nodes={'goto_pickup': 'PENDING', 'goto_dropoff': 'PENDING'}
t+  2.09s [robot>MD] state: lastNodeId='yegqune6dje55lhtgk4guvqjlm-n0-s2' seq=2 driving=True pos=(2.00,0.00) battery=99.9% errors=[]
t+  4.13s [robot>MD] state: lastNodeId='yegqune6dje55lhtgk4guvqjlm-n0-s4' seq=4 driving=False pos=(2.00,2.00) battery=99.9% errors=[]
t+  4.16s [MD>robot] order yegqune6dje55lhtgk4guvqjlm-n1 (update 0): 2 nodes ['yegqune6dje55lhtgk4guvqjlm-n1-s0', 'yegqune6dje55lhtgk4guvqjlm-n1-s2']
t+  4.23s [robot>MD] state: lastNodeId='yegqune6dje55lhtgk4guvqjlm-n1-s0' seq=0 driving=True pos=(2.00,2.00) battery=99.9% errors=[]
t+  5.15s [MD api ] mission RUNNING nodes={'goto_pickup': 'COMPLETED', 'goto_dropoff': 'PENDING'}
t+  6.20s [robot>MD] state: lastNodeId='yegqune6dje55lhtgk4guvqjlm-n1-s2' seq=2 driving=False pos=(0.00,2.00) battery=99.9% errors=[]
t+  7.19s [MD api ] mission COMPLETED nodes={'goto_pickup': 'COMPLETED', 'goto_dropoff': 'COMPLETED'}
t+  7.20s [MD api ] final robot pose=(0.00,2.00) state=IDLE
RESULT: mission COMPLETED
```

## Interop findings

1. **MD publishes instant actions in the VDA 5050 1.x shape** — the array is
   named `instantActions` (items use `actionType`), while the message is
   stamped `version: 2.0.0`. The official 2.x schemas name the array
   `actions`. The emulator now executes the 1.x-shaped list as a documented
   compatibility behavior while still reporting the deviation as a
   `validationError` WARNING (regression-tested in `test_compat.py`).
2. **MD redelivers the same instant action (~10/s) until a terminal status
   appears** in `actionStates`. Exposed a real robustness gap: redelivery of
   an already-known `actionId` is now idempotent instead of duplicating
   action states.
3. **MD's factsheet parser uses stub models** (`temporary: int` placeholders
   for `protocolLimits`/`protocolFeatures`/`agvGeometry`/`loadSpecification`),
   so it logs a warning about any spec-conformant factsheet. MD-side quirk;
   it still extracts `agvClass` and operates normally.
4. MD's order headers use a non-spec timestamp format (no `Z`, microseconds)
   and empty `manufacturer`/`serialNumber` — accepted, since the schemas only
   require them to be strings.

## Reproduce

The compose file and driver script live in this directory
(`isaac-mission-dispatch/`): start the emulator as above, `docker compose up
-d`, register the robot, then `uv run python validate.py`.
