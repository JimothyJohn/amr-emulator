# External conformance: OTTO/InOrbit/Ekumen VDA 5050 connector

Everything else in this repo validates VDA 5050 behavior against code from
this repo — consistent, but circular. This harness closes the loop against
an independent implementation of the robot side: the open-source
VDA 5050 ↔ ROS 2 connector that OTTO Motors, InOrbit, and Ekumen published
and that ships embedded in OTTO's product (release 2.28+).

- Upstream: <https://github.com/inorbit-ai/ros_amr_interop>
  (`vda5050_connector`, `vda5050_msgs`, `vda5050_serializer`), built
  **unmodified** at the commit pinned in the `Dockerfile`.
- Our side: `vda5050-master` (FleetMaster + MissionController) dispatching
  over this repo's embedded MQTT broker, protocol version 2.0.0 (the
  newest the connector supports).
- The connector's controller talks to a robot through an adapter; the
  `mock_adapter/` package stands in for Nav2 with a robot that teleports.
  The code under test — mqtt_bridge and controller — is upstream's.

## Run it

```sh
uv run interop/otto-vda5050/run_interop.py        # builds the image first time
uv run interop/otto-vda5050/run_interop.py --skip-build
```

Requires Docker. Exit 0 = a full order lifecycle (dispatch → running →
finished, with a HARD action), a base/horizon stitched update, and a
cancelOrder all succeed, and every message the connector published passed
validation against the official 2.0.0 schemas.

## Interop divergences found (connector quirks, spec-legal on our side)

- **`nodePosition.theta` is required by the connector.** The official
  2.0.0 order schema marks `theta` optional, but the bridge's
  `generate_vda_order_msg` does `float(node["node_position"]["theta"])`
  unconditionally and drops the whole order with
  `Ignoring invalid VDA5050 message: 'theta'` when absent. The harness
  therefore sets an explicit theta on every waypoint.
- **ONLINE is reported before orders can be received.** The bridge
  publishes `connection: ONLINE` as soon as MQTT connects, while the
  controller can still be blocked waiting for its adapter — an order
  dispatched in that window is dropped without any rejection. The harness
  gates dispatch on the first `state` message, which the controller only
  publishes once fully initialized.
- **No schema-valid 2.0.0 instant action can reach the connector at all.**
  The official 2.0.0 instantActions schema *requires* `actionName` (and has
  no `actionType`); the bridge kwarg-splats the deserialized JSON into
  `vda5050_msgs/Action`, whose only field is `action_type`, so its MQTT
  thread dies with `AssertionError: Invalid arguments passed to
  constructor: action_name` — killing the robot's MQTT link until restart.
  cancelOrder is therefore untestable against this connector on 2.0.0. The
  harness's phase 3 sends a schema-valid cancelOrder and PASSES only while
  this failure reproduces; when upstream fixes it, the probe fails loudly
  so the note (and the probe) get retired and the CANCELED assertion
  restored.

Ready-to-file issue bodies for all three: `UPSTREAM_ISSUES.md` in this
directory. Record the issue URLs here once filed.
