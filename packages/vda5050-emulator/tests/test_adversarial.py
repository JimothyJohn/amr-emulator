"""Adversarial inputs: the robot must survive garbage, injection attempts and
concurrent abuse without a crash, without an invalid published message, and
while staying available for legitimate traffic."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from conftest import Stack, await_error, run, straight_order
from hypothesis import given, settings
from hypothesis import strategies as st
from vda5050_emulator import make_node
from vda5050_emulator.order import Situation, evaluate
from vda5050_emulator.validation import validation_errors
from vda5050_emulator.zones import point_in_polygon

GARBAGE = (
    b"",
    b"\x00\xff\xfe" * 100,
    b"not json at all",
    b"[]",
    b'"just a string"',
    b"{}",
    json.dumps({"orderId": 5, "orderUpdateId": "x", "nodes": {}, "edges": None}).encode(),
    ("{" + '"a":' * 2000 + "1" + "}" * 1).encode(),  # unbalanced nesting
    json.dumps({"orderId": "x\n\x1b[31minjected", "orderUpdateId": 0}).encode(),
)


def test_garbage_on_order_topic_never_kills_the_robot():
    async def body():
        async with Stack() as stack:
            for payload in GARBAGE:
                await stack.m.publish_raw("order", payload)
            await await_error(stack, "VALIDATION_FAILURE", timeout=10)
            # The robot still executes a legitimate order afterwards.
            nodes, edges = straight_order(n=2)
            await stack.m.send_order(nodes, edges, order_id="o-after")
            await stack.m.next_state(
                lambda s: s["orderId"] == "o-after" and s["lastNodeId"] == "n1",
                timeout=20,
            )
            # And every state it published on the way is still schema-valid.
            for doc in stack.published["state"]:
                assert not validation_errors("state", doc, tag="3.0.0")

    run(body())


def test_garbage_on_every_subscribed_topic():
    async def body():
        async with Stack() as stack:
            for name in ("instantActions", "zoneSet", "responses", "_emulator"):
                for payload in GARBAGE:
                    await stack.m.publish_raw(name, payload)
            aid = await stack.m.send_instant_action("stateRequest")
            await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)

    run(body())


def test_injection_strings_in_ids_are_data_not_code():
    async def body():
        async with Stack() as stack:
            evil = "evil\x00\n\x1b[2Jid"
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0),
                make_node(evil, 2, x=1.0, y=0.0),
            ]
            from vda5050_emulator import make_edge

            edges = [make_edge("e0", 1)]
            await stack.m.send_order(nodes, edges, order_id="o-evil")
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == evil and not s["nodeStates"], timeout=20
            )
            assert state["orderId"] == "o-evil"
            for doc in stack.published["state"]:
                assert not validation_errors("state", doc, tag="3.0.0")

    run(body())


def test_duplicate_action_ids_do_not_duplicate_states():
    async def body():
        async with Stack() as stack:
            from vda5050_emulator import make_action, make_edge

            action = make_action("detectObject")
            clone = dict(action)
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0, actions=[action]),
                make_node("n1", 2, x=1.0, y=0.0, actions=[clone]),
            ]
            edges = [make_edge("e0", 1)]
            await stack.m.send_order(nodes, edges, order_id="o-dup")
            state = await stack.m.next_state(lambda s: s["orderId"] == "o-dup", timeout=10)
            matching = [a for a in state["actionStates"] if a["actionId"] == action["actionId"]]
            assert len(matching) == 1

    run(body())


def test_concurrent_masters_one_robot():
    """Two masters race orders; the robot accepts exactly one and reports
    OTHER_ORDER_ACTIVE for the loser — no torn state."""

    async def body():
        async with Stack() as stack:
            from vda5050_emulator import MasterControl, make_action

            second = MasterControl(
                "127.0.0.1",
                stack.port,
                manufacturer=stack.r.topics.manufacturer,
                serial_number=stack.r.topics.serial_number,
                client_id="master-2",
            )
            await second.connect()
            hold = make_action(
                "waitForTrigger",
                blocking_type="HARD",
                parameters={"triggerType": ["FLEET_CONTROL"]},
            )
            hold_b = make_action(
                "waitForTrigger",
                blocking_type="HARD",
                parameters={"triggerType": ["FLEET_CONTROL"]},
            )
            nodes_a, edges_a = straight_order(n=2)
            nodes_a[1]["actions"] = [hold]
            nodes_b, edges_b = straight_order(n=2)
            nodes_b[1]["actions"] = [hold_b]
            await asyncio.gather(
                stack.m.send_order(nodes_a, edges_a, order_id="o-A"),
                second.send_order(nodes_b, edges_b, order_id="o-B"),
            )
            state = await stack.m.next_state(
                lambda s: (
                    s["orderId"] in ("o-A", "o-B")
                    and any(e["errorType"] == "OTHER_ORDER_ACTIVE" for e in s["errors"])
                ),
                timeout=20,
            )
            winner = state["orderId"]
            assert winner in ("o-A", "o-B")
            later = await stack.m.next_state(timeout=5)
            assert later["orderId"] == winner, "accepted order must not flip"
            await second.disconnect()

    run(body())


def test_parallel_instant_actions_while_driving():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=3)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            ids = await asyncio.gather(
                *(stack.m.send_instant_action("stateRequest") for _ in range(10))
            )
            for aid in ids:
                await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=20
            )

    run(body())


# ---------------------------------------------------------------------------
# Property tests on the pure logic (deterministic, no I/O).


@st.composite
def order_graphs(draw):
    n = draw(st.integers(min_value=1, max_value=6))
    base = draw(st.integers(min_value=1, max_value=n))
    start_seq = draw(st.integers(min_value=0, max_value=3)) * 2
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for i in range(n):
        nodes.append(
            {
                "nodeId": f"n{i}",
                "sequenceId": start_seq + 2 * i,
                "released": i < base,
                "actions": [],
            }
        )
        if i:
            edges.append(
                {
                    "edgeId": f"e{i}",
                    "sequenceId": start_seq + 2 * i - 1,
                    "released": i < base,
                    "actions": [],
                }
            )
    order = {
        "orderId": draw(st.text(min_size=1, max_size=8)),
        "orderUpdateId": draw(st.integers(min_value=0, max_value=3)),
        "nodes": nodes,
        "edges": edges,
    }
    if draw(st.booleans()):  # random mutation to exercise rejects
        mutation = draw(st.integers(min_value=0, max_value=3))
        if mutation == 0 and edges:
            edges[draw(st.integers(0, len(edges) - 1))]["sequenceId"] += 2
        elif mutation == 1:
            nodes[draw(st.integers(0, len(nodes) - 1))]["released"] = draw(st.booleans())
        elif mutation == 2 and edges:
            del edges[draw(st.integers(0, len(edges) - 1))]
        elif mutation == 3:
            nodes[0]["sequenceId"] += 1
    return order


@given(order_graphs())
@settings(max_examples=300, deadline=None)
def test_evaluate_total_and_closed(order):
    """evaluate() never raises and always returns a definite verdict."""
    situation = Situation(idle=True, position=(0.0, 0.0), known_maps=frozenset({"map-0"}))
    decision = evaluate(order, situation)
    assert decision.verdict in ("accept", "ignore", "reject")
    if decision.verdict == "reject":
        assert decision.error_key


@given(
    st.lists(
        st.tuples(st.floats(-100, 100, allow_nan=False), st.floats(-100, 100, allow_nan=False)),
        min_size=3,
        max_size=12,
    ),
    st.floats(-150, 150, allow_nan=False),
    st.floats(-150, 150, allow_nan=False),
)
@settings(max_examples=300, deadline=None)
def test_point_in_polygon_total(vertices, x, y):
    polygon = [{"x": vx, "y": vy} for vx, vy in vertices]
    result = point_in_polygon(x, y, polygon)
    assert result in (True, False)
