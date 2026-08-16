"""Per-version wire-format faithfulness: 2.0.0 / 2.1.0 / 3.0.0 side by side.

Each protocol generation gets the vocabulary of its own official schema —
topic prefixes, state field names, connection enums, error names — and every
message a robot publishes must validate against the schema of the version it
speaks, never a neighbouring one.
"""

from __future__ import annotations

import asyncio
import json

import pytest
from conftest import Stack, await_error, run
from vda5050_emulator import MQTTClient, make_action, make_edge, make_node
from vda5050_emulator.validation import validation_errors

ALL = ("2.0.0", "2.1.0", "3.0.0")
V2 = ("2.0.0", "2.1.0")


# 2.0.0 wire quirks handled by the implementation (regression-tested here):
# instant actions carry `actionName` (master emits it, robot reads it), and
# nodeStates omit nodePosition when the order's position lacks theta (the
# 2.0.0 schema requires theta inside nodeState.nodePosition).


async def send_instant(stack, version, action_type, parameters=None):
    return await stack.m.send_instant_action(action_type, parameters=parameters)


def order_with_theta(version, order_id, n=3):
    nodes = [make_node(f"n{i}", 2 * i, x=float(i), y=0.0, theta=0.0) for i in range(n)]
    edges = [
        make_edge(
            f"e{i}",
            2 * i + 1,
            start_node_id=f"n{i}",
            end_node_id=f"n{i + 1}",
            version=version,
        )
        for i in range(n - 1)
    ]
    return nodes, edges


@pytest.mark.parametrize("version", ALL)
def test_topic_prefix_matches_family(version):
    async def body():
        async with Stack(version) as stack:
            prefix = stack.r.topics.prefix
            if version.startswith("2."):
                assert prefix.startswith("uagv/v2/")
            else:
                assert prefix.startswith("vda5050/v3/")

    run(body())


@pytest.mark.parametrize("version", ALL)
def test_state_vocabulary_and_schema(version):
    async def body():
        async with Stack(version) as stack:
            nodes, edges = order_with_theta(version, "o-vocab", n=2)
            await stack.m.send_order(nodes, edges, order_id="o-vocab")
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n1" and not s["nodeStates"], timeout=15
            )
            if version.startswith("2."):
                assert "agvPosition" in state and "batteryState" in state
                assert "eStop" in state["safetyState"]
                assert "positionInitialized" in state["agvPosition"]
                assert "mobileRobotPosition" not in state
            else:
                assert "mobileRobotPosition" in state and "powerSupply" in state
                assert "activeEmergencyStop" in state["safetyState"]
                assert state["mobileRobotPosition"]["localized"] is True
            for doc in stack.m.states:
                assert validation_errors("state", doc, tag=version) == []

    run(body())


@pytest.mark.parametrize("version", ALL)
def test_connection_lifecycle_and_retained_will(version):
    async def body():
        async with Stack(version) as stack:
            assert stack.m.connections[0]["connectionState"] == "ONLINE"
            for doc in stack.m.connections:
                assert validation_errors("connection", doc, tag=version) == []
            broken = "CONNECTIONBROKEN" if version.startswith("2.") else "CONNECTION_BROKEN"
            await stack.r.drop_connection()
            probe = MQTTClient(f"probe-{version}", "127.0.0.1", stack.port)
            await probe.connect()
            await probe.subscribe(stack.r.topics.topic("connection"))
            message = await asyncio.wait_for(probe.messages.get(), timeout=5)
            doc = json.loads(message.payload.decode())
            assert doc["connectionState"] == broken
            assert validation_errors("connection", doc, tag=version) == []
            await probe.disconnect()

    run(body())


@pytest.mark.parametrize(
    ("version", "error_type"),
    [("2.0.0", "noOrderToCancel"), ("2.1.0", "noOrderToCancel"), ("3.0.0", "NO_ORDER_TO_CANCEL")],
)
def test_cancel_idle_error_vocabulary(version, error_type):
    async def body():
        async with Stack(version) as stack:
            action = await send_instant(stack, version, "cancelOrder")
            final = await stack.m.action_status(action, statuses=("FINISHED", "FAILED"))
            assert final["actionStatus"] == "FAILED"
            error = await await_error(stack, error_type)
            assert error["errorLevel"] == "WARNING"

    run(body())


@pytest.mark.parametrize("version", V2)
def test_v2_wire_error_levels_only_warning_or_fatal(version):
    async def body():
        async with Stack(version) as stack:
            await send_instant(stack, version, "cancelOrder")  # noOrderToCancel WARNING
            await await_error(stack, "noOrderToCancel")
            stack.r.inject(localized=False)  # localizationError FATAL on the 2.x wire
            await await_error(stack, "localizationError")
            levels = {e["errorLevel"] for s in stack.m.states for e in s.get("errors", [])}
            assert levels <= {"WARNING", "FATAL"}, levels

    run(body())


@pytest.mark.parametrize("version", ALL)
def test_factsheet_retained_and_schema_valid(version):
    async def body():
        async with Stack(version) as stack:
            # The factsheet is retained: a late subscriber (the master connects
            # after the robot started) still received it.
            assert stack.m.factsheets, "retained factsheet not delivered"
            doc = stack.m.factsheets[0]
            assert validation_errors("factsheet", doc, tag=version) == []
            if version.startswith("2."):
                assert "agvActions" in doc["protocolFeatures"]
                assert "agvGeometry" in doc
                assert "agvKinematic" in doc["typeSpecification"]
            else:
                ts = doc["typeSpecification"]
                assert "mobileRobotKinematics" in ts and "mobileRobotKinematic" in ts
                assert "mobileRobotActions" in doc["protocolFeatures"]

    run(body())


@pytest.mark.parametrize("version", V2)
def test_v2_single_blocking_type_is_schema_invalid(version):
    async def body():
        async with Stack(version) as stack:
            action = make_action("pick", blocking_type="SINGLE")
            nodes = [make_node("n0", 0, x=0.0, y=0.0, actions=[action])]
            doc = {
                "headerId": 0,
                "timestamp": "2026-01-01T00:00:00.000Z",
                "version": version,
                "manufacturer": stack.r.topics.manufacturer,
                "serialNumber": stack.r.topics.serial_number,
                "orderId": "o-single",
                "orderUpdateId": 0,
                "nodes": nodes,
                "edges": [],
            }
            await stack.m.publish_raw("order", doc)
            await await_error(stack, "validationError")
            latest = stack.m.states[-1]
            assert latest["orderId"] != "o-single"

    run(body())


@pytest.mark.parametrize("version", ALL)
def test_init_position_action_name_per_version(version):
    async def body():
        async with Stack(version) as stack:
            native = "initPosition" if version.startswith("2.") else "initializePosition"
            foreign = "initializePosition" if version.startswith("2.") else "initPosition"
            invalid_error = (
                "instantActionError" if version.startswith("2.") else "INVALID_INSTANT_ACTION"
            )
            action = await send_instant(
                stack,
                version,
                native,
                parameters={
                    "x": 9.0,
                    "y": 8.0,
                    "theta": 0.0,
                    "mapId": "map-0",
                    "lastNodeId": "n9",
                },
            )
            final = await stack.m.action_status(action, statuses=("FINISHED", "FAILED"))
            assert final["actionStatus"] == "FINISHED"
            position_field = "agvPosition" if version.startswith("2.") else "mobileRobotPosition"
            await stack.m.next_state(lambda s: s[position_field]["x"] == 9.0, timeout=10)

            bad = await send_instant(stack, version, foreign)
            final = await stack.m.action_status(bad, statuses=("FINISHED", "FAILED"))
            assert final["actionStatus"] == "FAILED"
            await await_error(stack, invalid_error)

    run(body())


@pytest.mark.parametrize("version", V2)
def test_v2_edges_require_start_and_end_node_ids(version):
    async def body():
        async with Stack(version) as stack:
            # Edge built for 3.0 lacks startNodeId/endNodeId -> 2.x schema reject.
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0),
                make_node("n1", 2, x=1.0, y=0.0),
            ]
            edges = [make_edge("e0", 1, version="3.0.0")]
            doc = {
                "headerId": 0,
                "timestamp": "2026-01-01T00:00:00.000Z",
                "version": version,
                "manufacturer": stack.r.topics.manufacturer,
                "serialNumber": stack.r.topics.serial_number,
                "orderId": "o-noends",
                "orderUpdateId": 0,
                "nodes": nodes,
                "edges": edges,
            }
            await stack.m.publish_raw("order", doc)
            await await_error(stack, "validationError")
            latest = stack.m.states[-1]
            assert latest["orderId"] != "o-noends"

    run(body())


@pytest.mark.parametrize("version", ALL)
def test_full_order_round_trip_per_version(version):
    async def body():
        async with Stack(version) as stack:
            nodes, edges = order_with_theta(version, "o-roundtrip", n=3)
            await stack.m.send_order(nodes, edges, order_id="o-roundtrip")
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=20
            )
            assert state["errors"] == []
            assert state["orderId"] == "o-roundtrip"

    run(body())
