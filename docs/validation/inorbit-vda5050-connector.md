# External validation: InOrbit/OTTO vda5050_connector

Date: 2026-08-16 · emulator branch `feat/vda5050-emulator` ·
[inorbit-ai/ros_amr_interop](https://github.com/inorbit-ai/ros_amr_interop) `vda5050_connector` (main, ROS 2 Humble)

Second external datapoint, complementary to the
[Isaac Mission Dispatch run](isaac-mission-dispatch.md): Mission Dispatch
validated the emulator's **robot side** against an external master; this run
validates the emulator's **master side** (`MasterControl`) and embedded broker
against an external robot-side implementation — the OTTO Motors + InOrbit
VDA5050 connector (mqtt_bridge + controller), with a ~100-line mock adapter
standing in for the ROS nav stack (no Gazebo needed).

## Setup

- The emulator's embedded broker on :1884 (the same process that served the
  Mission Dispatch run).
- `ros:humble` container: colcon-builds `vda5050_msgs` + `vda5050_serializer`
  + `vda5050_connector` from source, runs `mqtt_bridge` + `controller` +
  `mock_adapter.py` (assets in `inorbit-connector/`), MQTT pointed at
  `host.docker.internal:1884`.
- Driver: `validate_inorbit.py` uses `vda5050_emulator.MasterControl`
  (version 2.0.0, manufacturer `robots`, serial `robot_1`) to send a 3-node
  order with one attached `detectObject` action.

## What was validated

| Interop surface | Result |
|---|---|
| Their paho mqtt_bridge against the emulator's broker (incl. retained last-will handling) | connects; ONLINE/CONNECTIONBROKEN lifecycle observed |
| Our `MasterControl` order construction (2.0.0 wire shape) | accepted by their controller: "Order 'order-inorbit-1' with update id '0' accepted!" |
| Node traversal semantics | lastNodeId wp0 → wp1 → wp2, nodeStates 2 → 1 → 0 |
| Attached node action lifecycle | `detectObject` WAITING → FINISHED |
| Their state messages parsed by our `MasterControl` | operatingMode/battery/action states all read |

## Transcript

```
t+  0.00s [broker   ] reusing the vda5050-emulator's embedded broker already on :1884
t+  0.00s [master   ] MasterControl connected, waiting for the connector to appear
t+  3.29s [robot>us ] first state: operatingMode=AUTOMATIC battery=95.0%
t+  3.29s [robot>us ] connection: CONNECTIONBROKEN
t+  3.33s [us>robot ] order order-inorbit-1: 3 nodes, 2 edges, 1 attached action
t+  3.35s [robot>us ] state: lastNodeId='wp0' seq=0 nodeStates=2 actions=[('detectObject', 'WAITING')] errors=[]
t+  4.44s [robot>us ] state: lastNodeId='wp1' seq=2 nodeStates=1 actions=[('detectObject', 'WAITING')] errors=[]
t+  5.54s [robot>us ] state: lastNodeId='wp2' seq=4 nodeStates=0 actions=[('detectObject', 'WAITING')] errors=[]
t+  8.30s [robot>us ] state: lastNodeId='wp2' seq=4 nodeStates=0 actions=[('detectObject', 'FINISHED')] errors=[]
t+  8.30s [result   ] order complete: robot at wp2, all action states terminal

RESULT: order COMPLETED by InOrbit vda5050_connector
```

## Interop findings

1. **Their deserializer requires `nodePosition.theta`** (optional per the
   official order schema): an order without it is dropped with
   `Ignoring invalid VDA5050 message: 'theta'`. Masters driving this
   connector must always send theta.
2. **`allowedDeviationXY` is a scalar in 2.x** — our `make_node(deviation=…)`
   helper emits the 3.0.0 ellipse object; for 2.x targets set the float
   directly (helper improvement noted).
3. The initial `CONNECTIONBROKEN` in the transcript is the connector's
   retained last will from a previous container restart — correct MQTT will
   behavior on both sides, worth knowing when reading logs.

## Reproduce

Assets in `inorbit-connector/`. Clone `ros_amr_interop` (the repo bundles its
own `vda5050_msgs` — build that copy, not ipa320's), mount the packages plus
`mock_adapter.py`/`params.yaml`/`run_connector.sh` into `ros:humble` with
`--add-host host.docker.internal:host-gateway`, start the emulator's broker on
:1884, then `uv run python validate_inorbit.py`.
