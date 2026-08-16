"""The order acceptance process of Figure 8 and the rejection catalogue of
section 6.1.4, end to end over MQTT: every rejection produces exactly the
predefined error, keeps the previous order running, and clears when the next
order is accepted."""

from __future__ import annotations

import asyncio

from conftest import Stack, await_error, run, straight_order
from vda5050_emulator import make_action, make_edge, make_node


def test_accept_and_complete_with_horizon_extension():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=2, horizon=1)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            state = await stack.m.next_state(lambda s: bool(s.get("newBaseRequest")), timeout=20)
            assert state["lastNodeId"] == "n1"
            assert [n["nodeId"] for n in state["nodeStates"]] == ["n2"]
            # extend: stitch node n1 (seq 2) + released n2
            update_nodes = [
                make_node("n1", 2, x=1.0, y=0.0),
                make_node("n2", 4, x=2.0, y=0.0),
            ]
            update_edges = [make_edge("e1", 3)]
            await stack.m.send_order(update_nodes, update_edges, order_id="o-1", order_update_id=1)
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=20
            )
            assert state["orderUpdateId"] == 1
            assert not state["errors"]

    run(body())


def test_malformed_order_validation_failure():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=3)
            edges.pop()  # edge count no longer nodes-1
            await stack.m.publish_raw(
                "order",
                stack.m._with_header(
                    {"orderId": "bad", "orderUpdateId": 0, "nodes": nodes, "edges": edges},
                    topic="order",
                ),
            )
            error = await await_error(stack, "VALIDATION_FAILURE")
            assert error["errorLevel"] == "WARNING"
            state = await stack.m.next_state(timeout=5)
            assert state["orderId"] == ""  # order was not taken over

    run(body())


def test_new_order_with_nonzero_update_id_rejected():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order()
            await stack.m.send_order(nodes, edges, order_id="o-x", order_update_id=3)
            await await_error(stack, "VALIDATION_FAILURE")

    run(body())


def test_other_order_active():
    async def body():
        async with Stack() as stack:
            hard_wait = make_action(
                "waitForTrigger",
                blocking_type="HARD",
                parameters={"triggerType": ["FLEET_CONTROL"]},
            )
            nodes, edges = straight_order(n=2)
            nodes[1]["actions"] = [hard_wait]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(lambda s: s["lastNodeId"] == "n1", timeout=20)
            other_nodes, other_edges = straight_order(n=2)
            await stack.m.send_order(other_nodes, other_edges, order_id="o-2")
            error = await await_error(stack, "OTHER_ORDER_ACTIVE")
            assert error["errorLevel"] == "WARNING"
            state = await stack.m.next_state(timeout=5)
            assert state["orderId"] == "o-1"  # previous order kept

    run(body())


def test_outdated_and_same_order_update():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=2, horizon=1)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(lambda s: s["orderId"] == "o-1", timeout=10)
            update_nodes = [
                make_node("n1", 2, x=1.0, y=0.0),
                make_node("n2", 4, x=2.0, y=0.0),
            ]
            await stack.m.send_order(
                update_nodes, [make_edge("e1", 3)], order_id="o-1", order_update_id=1
            )
            await stack.m.next_state(lambda s: s["orderUpdateId"] == 1, timeout=10)
            # lower orderUpdateId -> OUTDATED_ORDER_UPDATE
            await stack.m.send_order(nodes, edges, order_id="o-1", order_update_id=0)
            await await_error(stack, "OUTDATED_ORDER_UPDATE")
            # same orderUpdateId, different content -> SAME_ORDER_UPDATE_ID
            different = [
                make_node("n1", 2, x=1.0, y=0.0),
                make_node("n9", 4, x=9.0, y=0.0),
            ]
            await stack.m.send_order(
                different, [make_edge("e1", 3)], order_id="o-1", order_update_id=1
            )
            await await_error(stack, "SAME_ORDER_UPDATE_ID")

    run(body())


def test_identical_resend_is_ignored_silently():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=2)
            first = await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(lambda s: s["orderId"] == "o-1", timeout=10)
            # bit-identical content (fresh header) -> no error, no restart
            await stack.m.publish_raw(
                "order",
                {**first, "headerId": 99, "timestamp": stack.m.clock.now_iso()},
            )
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n1" and not s["nodeStates"], timeout=20
            )
            state = await stack.m.next_state(timeout=5)
            assert not any(e["errorType"] == "SAME_ORDER_UPDATE_ID" for e in state["errors"])

    run(body())


def test_update_following_cancel_rejected():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=2, horizon=1)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(lambda s: s["orderId"] == "o-1", timeout=10)
            aid = await stack.m.send_instant_action("cancelOrder")
            await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)
            update_nodes = [
                make_node("n1", 2, x=1.0, y=0.0),
                make_node("n2", 4, x=2.0, y=0.0),
            ]
            await stack.m.send_order(
                update_nodes, [make_edge("e1", 3)], order_id="o-1", order_update_id=1
            )
            await await_error(stack, "ORDER_UPDATE_FOLLOWING_CANCEL")
            # a NEW order after cancellation is accepted
            fresh_nodes, fresh_edges = straight_order(n=2)
            await stack.m.send_order(fresh_nodes, fresh_edges, order_id="o-2")
            state = await stack.m.next_state(lambda s: s["orderId"] == "o-2", timeout=10)
            assert not any(
                e["errorType"] == "ORDER_UPDATE_FOLLOWING_CANCEL" for e in state["errors"]
            ), "errors must clear once a new order is accepted"

    run(body())


def test_start_node_out_of_range():
    async def body():
        async with Stack() as stack:
            nodes = [
                make_node("far", 0, x=50.0, y=50.0, deviation=0.1),
                make_node("far2", 2, x=51.0, y=50.0),
            ]
            edges = [make_edge("e0", 1)]
            await stack.m.send_order(nodes, edges, order_id="o-far")
            await await_error(stack, "START_NODE_OUT_OF_RANGE")

    run(body())


def test_extended_deviation_makes_far_start_acceptable():
    async def body():
        async with Stack() as stack:
            nodes = [
                make_node("far", 0, x=50.0, y=50.0, deviation=100.0),
                make_node("far2", 2, x=51.0, y=50.0),
            ]
            edges = [make_edge("e0", 1)]
            await stack.m.send_order(nodes, edges, order_id="o-far")
            state = await stack.m.next_state(lambda s: s["orderId"] == "o-far", timeout=10)
            assert state["lastNodeId"] == "far"

    run(body())


def test_unknown_map_id():
    async def body():
        async with Stack() as stack:
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0, map_id="map-unknown"),
                make_node("n1", 2, x=1.0, y=0.0, map_id="map-unknown"),
            ]
            edges = [make_edge("e0", 1)]
            await stack.m.send_order(nodes, edges, order_id="o-map")
            error = await await_error(stack, "UNKNOWN_MAP_ID")
            assert error["errorLevel"] == "WARNING"

    run(body())


def test_unsupported_order_action():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=2)
            nodes[1]["actions"] = [make_action("teleportToMars")]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await await_error(stack, "INVALID_ORDER_ACTION")

    run(body())


def test_order_rejected_in_manual_mode():
    async def body():
        async with Stack() as stack:
            stack.r.inject(operating_mode="MANUAL")
            await stack.m.next_state(lambda s: s["operatingMode"] == "MANUAL", timeout=10)
            nodes, edges = straight_order(n=2)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await await_error(stack, "MOBILE_ROBOT_NOT_AVAILABLE")
            stack.r.inject(operating_mode="AUTOMATIC")
            await stack.m.send_order(nodes, edges, order_id="o-2")
            await stack.m.next_state(lambda s: s["orderId"] == "o-2", timeout=10)

    run(body())


def test_stitching_mismatch_rejected():
    async def body():
        async with Stack() as stack:
            nodes, edges = straight_order(n=2, horizon=1)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(lambda s: s["orderId"] == "o-1", timeout=10)
            wrong_stitch = [
                make_node("nope", 2, x=1.0, y=0.0),
                make_node("n2", 4, x=2.0, y=0.0),
            ]
            await stack.m.send_order(
                wrong_stitch, [make_edge("e1", 3)], order_id="o-1", order_update_id=1
            )
            await await_error(stack, "VALIDATION_FAILURE")

    run(body())


def test_cancel_order_mid_drive_clears_states_keeps_ids():
    async def body():
        async with Stack() as stack:
            wait = make_action(
                "waitForTrigger",
                blocking_type="HARD",
                parameters={"triggerType": ["FLEET_CONTROL"]},
            )
            nodes, edges = straight_order(n=3)
            nodes[1]["actions"] = [wait]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.action_status(wait["actionId"], statuses=("RUNNING",), timeout=20)
            aid = await stack.m.send_instant_action("cancelOrder")
            await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)
            state = await stack.m.next_state(
                lambda s: (
                    s["orderId"] == "o-1"
                    and not s["nodeStates"]
                    and not s["edgeStates"]
                    and any(
                        a["actionId"] == wait["actionId"] and a["actionStatus"] == "FAILED"
                        for a in s["actionStates"]
                    )
                ),
                timeout=10,
            )
            assert state["orderId"] == "o-1"  # ids are kept (6.1.3)
            cancelled = next(a for a in state["actionStates"] if a["actionId"] == wait["actionId"])
            assert cancelled["actionStatus"] == "FAILED"

    run(body())


def test_horizon_replacement_drops_old_horizon_action_states():
    async def body():
        async with Stack() as stack:
            horizon_action = make_action("detectObject")
            nodes, edges = straight_order(n=2, horizon=1)
            nodes[2]["actions"] = [horizon_action]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(
                lambda s: any(
                    a["actionId"] == horizon_action["actionId"] for a in s["actionStates"]
                ),
                timeout=10,
            )
            # replace horizon with a different node, no actions
            update_nodes = [
                make_node("n1", 2, x=1.0, y=0.0),
                make_node("alt", 4, x=1.0, y=5.0, released=False),
            ]
            update_edges = [make_edge("e-alt", 3, released=False)]
            await stack.m.send_order(update_nodes, update_edges, order_id="o-1", order_update_id=1)
            state = await stack.m.next_state(lambda s: s["orderUpdateId"] == 1, timeout=10)
            assert not any(
                a["actionId"] == horizon_action["actionId"] for a in state["actionStates"]
            ), "horizon replacement must remove the dropped actions' states (6.6.9.1)"
            assert any(n["nodeId"] == "alt" for n in state["nodeStates"])

    run(body())


def test_idle_after_completion_accepts_next_order():
    async def body():
        async with Stack() as stack:
            for i, order_id in enumerate(("o-1", "o-2")):
                nodes, edges = straight_order(n=2, x0=float(i))
                await stack.m.send_order(nodes, edges, order_id=order_id)
                await stack.m.next_state(
                    lambda s, oid=order_id: (
                        s["orderId"] == oid and s["lastNodeId"] == "n1" and not s["nodeStates"]
                    ),
                    timeout=20,
                )
                await asyncio.sleep(0.05)

    run(body())
