"""Robot torture: order storms, advertised-limit enforcement, action churn,
hostile identifiers, fault storms, hibernation races and degenerate zone
geometry. The bar: a manufacturing-floor robot that never wedges and never
publishes an invalid or inconsistent state, no matter the abuse."""

from __future__ import annotations

import asyncio
import random

from vda5050_emulator import make_action, make_edge, make_node
from vda5050_emulator.validation import validation_errors
from vda5050_emulator.zones import is_simple_polygon
from vda_harness import Stack, await_error, run, straight_order


def test_hundred_sequential_orders_all_complete():
    async def body():
        async with Stack(scale=400.0, min_state_interval=0.01) as stack:
            for i in range(100):
                nodes, edges = straight_order(n=2, x0=float(i % 7))
                stack.r.teleport(x=float(i % 7), y=0.0)
                await stack.m.send_order(nodes, edges, order_id=f"storm-{i}")
                await stack.m.next_state(
                    lambda s, oid=f"storm-{i}": (
                        s["orderId"] == oid and s["lastNodeId"] == "n1" and not s["nodeStates"]
                    ),
                    timeout=15,
                )
            state = await stack.m.next_state(timeout=5)
            assert not validation_errors("state", state, tag="3.0.0")

    run(body(), timeout=120)


def test_out_of_order_update_storm_converges():
    async def body():
        async with Stack(scale=400.0) as stack:
            nodes, edges = straight_order(n=2, horizon=1)
            await stack.m.send_order(nodes, edges, order_id="conflict")
            await stack.m.next_state(lambda s: s["orderId"] == "conflict", timeout=10)
            rng = random.Random(42)  # noqa: S311 — deterministic test fuzz, not crypto
            update_ids = [rng.randint(0, 60) for _ in range(50)]
            for uid in update_ids:
                # Deliberately wrong stitches and shuffled updateIds: every
                # one must be rejected or ignored without wedging the robot.
                bogus_nodes = [
                    make_node("nowhere", 2, x=1.0, y=0.0, theta=0.0),
                    make_node("nowhere2", 4, x=2.0, y=0.0),
                ]
                await stack.m.publish_raw(
                    "order",
                    stack.m._with_header(
                        {
                            "orderId": "conflict",
                            "orderUpdateId": uid,
                            "nodes": bogus_nodes,
                            "edges": [make_edge("be", 3)],
                        },
                        topic="order",
                    ),
                )
            # Robot still answers, still on a sane update id, state valid.
            aid = await stack.m.send_instant_action("stateRequest")
            await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)
            state = await stack.m.next_state(timeout=5)
            assert state["orderId"] == "conflict"
            assert state["orderUpdateId"] in (0, *update_ids)
            assert not validation_errors("state", state, tag="3.0.0")

    run(body(), timeout=60)


def test_giant_order_within_limit_completes():
    async def body():
        async with Stack(scale=2000.0, min_state_interval=0.5) as stack:
            n = 500
            nodes = [
                make_node(f"g{i}", 2 * i, x=float(i) * 0.2, y=0.0, theta=0.0) for i in range(n)
            ]
            edges = [make_edge(f"ge{i}", 2 * i + 1) for i in range(n - 1)]
            await stack.m.send_order(nodes, edges, order_id="giant")
            state = await stack.m.next_state(lambda s: s["orderId"] == "giant", timeout=15)
            assert len(state["nodeStates"]) == n - 1  # first node not reported
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == f"g{n - 1}" and not s["nodeStates"],
                timeout=90,
            )

    run(body(), timeout=120)


def test_order_beyond_advertised_limit_rejected():
    async def body():
        async with Stack() as stack:
            n = 1001
            nodes = [make_node(f"h{i}", 2 * i, x=float(i) * 0.01, y=0.0) for i in range(n)]
            edges = [make_edge(f"he{i}", 2 * i + 1) for i in range(n - 1)]
            await stack.m.send_order(nodes, edges, order_id="too-big")
            error = await await_error(stack, "INSUFFICIENT_MEMORY", timeout=15)
            assert error["errorLevel"] == "URGENT"
            state = await stack.m.next_state(timeout=5)
            assert state["orderId"] == ""  # never taken over

    run(body(), timeout=60)


def test_pause_churn_hundred_toggles_mid_drive():
    async def body():
        async with Stack(scale=100.0) as stack:
            nodes, edges = straight_order(n=3)
            await stack.m.send_order(nodes, edges, order_id="churn")
            await stack.m.next_state(lambda s: s["orderId"] == "churn", timeout=10)
            for i in range(100):
                await stack.m.send_instant_action("startPause" if i % 2 == 0 else "stopPause")
            # Ended on stopPause (i=99): the drive must finish.
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=30
            )
            assert state["paused"] is False
            assert not validation_errors("state", state, tag="3.0.0")

    run(body(), timeout=90)


def test_cancel_racing_fresh_orders_never_wedges():
    async def body():
        async with Stack(scale=200.0) as stack:
            for i in range(20):
                nodes, edges = straight_order(n=2, x0=0.0)
                stack.r.teleport(x=0.0, y=0.0)
                await asyncio.gather(
                    stack.m.send_order(nodes, edges, order_id=f"race-{i}"),
                    stack.m.send_instant_action("cancelOrder"),
                )
                await asyncio.sleep(0.03)
            # Whatever the interleavings did, the robot must still work.
            stack.r.teleport(x=0.0, y=0.0)
            nodes, edges = straight_order(n=2, x0=0.0)
            await stack.m.send_order(nodes, edges, order_id="race-final")
            await stack.m.next_state(
                lambda s: (
                    s["orderId"] == "race-final" and s["lastNodeId"] == "n1" and not s["nodeStates"]
                ),
                timeout=20,
            )

    run(body(), timeout=90)


def test_hostile_identifiers_are_data():
    async def body():
        async with Stack() as stack:
            evil_order = "A" * 1000 + "​‮../../etc/passwd\"',}{"
            evil_node = "ن هاية‍😾\\x00"
            nodes = [
                make_node("start", 0, x=0.0, y=0.0),
                make_node(evil_node, 2, x=1.0, y=0.0),
            ]
            edges = [make_edge("e0", 1)]
            await stack.m.send_order(nodes, edges, order_id=evil_order)
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == evil_node and not s["nodeStates"],
                timeout=20,
            )
            assert state["orderId"] == evil_order  # echoed intact, everywhere
            for doc in stack.published["state"]:
                assert not validation_errors("state", doc, tag="3.0.0")

    run(body())


def test_fault_storm_then_recovery_completes_order():
    async def body():
        async with Stack(scale=100.0) as stack:
            nodes, edges = straight_order(n=3)
            await stack.m.send_order(nodes, edges, order_id="faulty")
            await stack.m.next_state(lambda s: s["orderId"] == "faulty", timeout=10)
            for i in range(40):  # ~2s of chaos at 50ms per toggle
                stack.r.inject(
                    emergency_stop="MANUAL" if i % 2 else "NONE",
                    field_violation=bool(i % 3),
                    localized=bool(i % 5 != 0),
                    battery={"level": 5 + (i * 7) % 90},
                )
                await asyncio.sleep(0.05)
            stack.r.inject(emergency_stop="NONE", field_violation=False, localized=True)
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=30
            )
            assert state["safetyState"]["activeEmergencyStop"] == "NONE"
            assert not any(e["errorType"] == "LOCALIZATION_ERROR" for e in state["errors"])

    run(body(), timeout=90)


def test_hibernation_mid_drive_and_past_wakeup():
    async def body():
        async with Stack(scale=50.0) as stack:
            nodes, edges = straight_order(n=3)
            nodes[1]["actions"] = [make_action("detectObject")]
            await stack.m.send_order(nodes, edges, order_id="sleepy")
            await stack.m.next_state(lambda s: s["driving"], timeout=15)
            hib = await stack.m.send_instant_action(
                "startHibernation",
                parameters={"wakeUpTime": "2000-01-01T00:00:00.000Z"},  # past
            )
            await stack.m.action_status(hib, statuses=("FINISHED",), timeout=15)
            await stack.m.next_state(
                lambda s: not s["nodeStates"] and not s["edgeStates"], timeout=10
            )
            # Race stopHibernation against the (already-due) auto-wake.
            stop = await stack.m.send_instant_action("stopHibernation")
            for _ in range(200):
                if stack.r.hibernating is False:
                    break
                await asyncio.sleep(0.05)
            assert stack.r.hibernating is False
            # ONLINE retained, robot accepts orders again.
            stack.r.teleport(x=0.0, y=0.0)
            nodes2, edges2 = straight_order(n=2)
            await stack.m.send_order(nodes2, edges2, order_id="awake")
            await stack.m.next_state(
                lambda s: s["orderId"] == "awake" and s["lastNodeId"] == "n1",
                timeout=20,
            )
            del stop

    run(body(), timeout=60)


def test_zone_polygon_validation_matrix():
    assert not is_simple_polygon([])
    assert not is_simple_polygon([{"x": 0, "y": 0}, {"x": 1, "y": 1}])
    # Bowtie: self-intersecting.
    assert not is_simple_polygon(
        [{"x": 0, "y": 0}, {"x": 2, "y": 2}, {"x": 2, "y": 0}, {"x": 0, "y": 2}]
    )
    # Rectangle with a collinear midpoint on one edge: still simple.
    assert is_simple_polygon(
        [
            {"x": 0, "y": 0},
            {"x": 1, "y": 0},
            {"x": 2, "y": 0},
            {"x": 2, "y": 2},
            {"x": 0, "y": 2},
        ]
    )
    # Degenerate sliver: simple, allowed.
    assert is_simple_polygon([{"x": 0, "y": 0}, {"x": 5, "y": 0.001}, {"x": 5, "y": 0}])


def test_self_intersecting_zone_rejected_on_wire():
    async def body():
        async with Stack() as stack:
            await stack.m.send_zone_set(
                {
                    "zoneSetId": "zs-bowtie",
                    "mapId": "map-0",
                    "zones": [
                        {
                            "zoneId": "bowtie",
                            "zoneType": "BLOCKED",
                            "vertices": [
                                {"x": 0.0, "y": 0.0},
                                {"x": 2.0, "y": 2.0},
                                {"x": 2.0, "y": 0.0},
                                {"x": 0.0, "y": 2.0},
                            ],
                        }
                    ],
                }
            )
            await await_error(stack, "VALIDATION_FAILURE", timeout=10)
            state = await stack.m.next_state(timeout=5)
            assert not any(z["zoneSetId"] == "zs-bowtie" for z in state.get("zoneSets", [])), (
                "self-intersecting polygon must not be stored (spec 7.6)"
            )

    run(body())


def test_blocked_zone_covering_path_start_reports_and_holds():
    async def body():
        async with Stack() as stack:
            await stack.m.send_zone_set(
                {
                    "zoneSetId": "zs-start",
                    "mapId": "map-0",
                    "zones": [
                        {
                            "zoneId": "z-start",
                            "zoneType": "BLOCKED",
                            "vertices": [
                                {"x": -0.5, "y": -0.5},
                                {"x": 0.6, "y": -0.5},
                                {"x": 0.6, "y": 0.5},
                                {"x": -0.5, "y": 0.5},
                            ],
                        }
                    ],
                }
            )
            enable = await stack.m.send_instant_action(
                "enableZoneSet", parameters={"zoneSetId": "zs-start"}
            )
            await stack.m.action_status(enable, statuses=("FINISHED",), timeout=10)
            nodes, edges = straight_order(n=2)
            await stack.m.send_order(nodes, edges, order_id="from-inside")
            state = await stack.m.next_state(
                lambda s: any(
                    e["errorType"] in ("BLOCKED_ZONE_VIOLATION", "NODE_UNREACHABLE")
                    for e in s["errors"]
                ),
                timeout=15,
            )
            assert state["driving"] is False

    run(body())
