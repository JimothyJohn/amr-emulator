# Ready-to-file issues for inorbit-ai/ros_amr_interop

Three defects found by this repo's conformance harness
(`interop/otto-vda5050/`, connector pinned at `9536d90a`, humble-devel,
VDA 5050 2.0.0). Each section below is a complete issue body — file them
verbatim at <https://github.com/inorbit-ai/ros_amr_interop/issues>, then
record the issue URLs next to the corresponding bullet in `README.md` so
the expected-divergence probe's retirement has a paper trail.

---

## Issue 1 — mqtt_bridge drops orders whose nodePosition omits optional `theta`

**Title:** `mqtt_bridge silently drops orders missing the optional nodePosition.theta`

The official VDA 5050 2.0.0 `order.schema.json` marks `nodePosition.theta`
optional (only `x`, `y`, `mapId` are required). The bridge's
`generate_vda_order_msg` force-casts it unconditionally:

```python
for k in ["x", "y", "theta"]:
    node["node_position"][k] = float(node["node_position"][k])
```

A schema-valid order without `theta` raises `KeyError`, is caught by the
generic handler in `on_message_mqtt`, and the whole order is discarded with
only `Ignoring invalid VDA5050 message: 'theta'.` — the master control sees
no rejection on the wire, just silence.

**Repro:** publish any 2.0.0 order whose nodes carry `{"x": 0, "y": 0,
"mapId": "map"}` positions. **Expected:** order accepted (or rejected with
a VDA error the MC can see). **Actual:** dropped silently.

**Suggested fix:** `node["node_position"].setdefault("theta", 0.0)` (and
treat the other optional NodePosition fields the same way), or reject with
a proper `validationError` on the state topic.

---

## Issue 2 — connection ONLINE is published before the controller can receive orders

**Title:** `ONLINE reported while the controller is still waiting for its adapter — orders sent in that window vanish`

`mqtt_bridge` publishes `connection: ONLINE` as soon as the MQTT session is
up. The controller node, however, blocks in `_configure_action_clients` /
`_configure_service_clients` until the adapter's servers exist — and its
`order` subscription isn't active yet. A master control that (correctly)
treats ONLINE as "robot ready" and dispatches immediately publishes into a
ROS topic with no subscriber: the order is lost with no rejection and no
error.

**Repro:** start bridge+controller while the adapter takes a few seconds to
come up; publish an order immediately after ONLINE. **Expected:** the order
is processed once the controller is ready, or the robot stays OFFLINE until
it can accept orders. **Actual:** the order vanishes.

**Suggested fix:** publish ONLINE only after the controller reports ready
(e.g. controller → bridge readiness topic), or have the bridge queue
MC-bound messages until the controller's subscriptions are up.

---

## Issue 3 — any schema-valid 2.0.0 instant action kills the MQTT thread (`actionName`)

**Title:** `AssertionError: Invalid arguments passed to constructor: action_name — schema-valid 2.0.0 instantActions crash the bridge`

The official 2.0.0 `instantActions.schema.json` **requires** `actionName`
on every action (there is no `actionType` property in that version).
`generate_vda_instant_action_msg` splats the deserialized JSON straight
into the ROS message constructor:

```python
vda_instant_action["actions"] = [
    VDAAction(**action) for action in vda_instant_action[instant_actions_field]
]
```

`vda5050_msgs/Action` only has `action_type`, so `action_name` raises
`AssertionError` inside the paho callback, which kills the network-loop
thread:

```
File ".../mqtt_bridge.py", line 186, in <listcomp>
    VDAAction(**action) for action in vda_instant_action[instant_actions_field]
File ".../vda5050_msgs/msg/_action.py", line 114, in __init__
    assert all('_' + key in self.__slots__ for key in kwargs.keys())
AssertionError: Invalid arguments passed to constructor: action_name
```

After that the robot is deaf until restart (no LWT fires — the TCP session
is still open, only the thread is dead). Consequence: **no schema-valid
2.0.0 instant action — including cancelOrder — can ever reach this
connector.**

**Repro:** publish
`{"headerId": 1, "timestamp": "...", "version": "2.0.0", "manufacturer": "...", "serialNumber": "...", "actions": [{"actionId": "a1", "actionName": "cancelOrder", "blockingType": "NONE"}]}`
on the instantActions topic. **Expected:** cancelOrder processed.
**Actual:** bridge MQTT thread dies.

**Suggested fix:** map `action_name` → `action_type` for 2.0.0 payloads
(mirroring the existing v1 `instant_actions` field HACK), and wrap the
conversion in a try/except that logs and survives instead of letting
exceptions escape into the paho thread.
