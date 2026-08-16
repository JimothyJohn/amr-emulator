"""Zones (VDA 5050 3.0.0, section 6.4) and the request/response mechanism (6.9).

Covers zone-set storage/enable/duplicate handling, the RELEASE gate
(REQUESTED -> GRANTED/REJECTED/REVOKED), BLOCKED refusal, SPEED_LIMIT
enforcement measured in simulated time, ACTION zone execution, and robustness
against schema-invalid zone sets.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from conftest import Stack, await_error, run, straight_order


def rect_zone(zone_id: str, zone_type: str, x0: float, x1: float, **extra) -> dict:
    zone = {
        "zoneId": zone_id,
        "zoneType": zone_type,
        "vertices": [
            {"x": x0, "y": -1.0},
            {"x": x1, "y": -1.0},
            {"x": x1, "y": 1.0},
            {"x": x0, "y": 1.0},
        ],
    }
    zone.update(extra)
    return zone


def zone_set(zone_set_id: str, zones: list[dict], map_id: str = "map-0") -> dict:
    return {"zoneSetId": zone_set_id, "mapId": map_id, "zones": zones}


async def enable(stack: Stack, zone_set_id: str) -> None:
    action = await stack.m.send_instant_action(
        "enableZoneSet", parameters={"zoneSetId": zone_set_id}
    )
    await stack.m.action_status(action, statuses=("FINISHED",), timeout=10)


def sim_ts(state: dict) -> float:
    return datetime.fromisoformat(state["timestamp"].replace("Z", "+00:00")).timestamp()


def test_zone_set_stored_disabled_then_enabled():
    async def body():
        async with Stack() as stack:
            await stack.m.send_zone_set(zone_set("zs-1", [rect_zone("z1", "BLOCKED", 90, 91)]))
            state = await stack.m.next_state(
                lambda s: any(z["zoneSetId"] == "zs-1" for z in s.get("zoneSets", []))
            )
            entry = next(z for z in state["zoneSets"] if z["zoneSetId"] == "zs-1")
            assert entry["zoneSetStatus"] == "DISABLED"
            assert entry["mapId"] == "map-0"
            await enable(stack, "zs-1")
            await stack.m.next_state(
                lambda s: any(
                    z["zoneSetId"] == "zs-1" and z["zoneSetStatus"] == "ENABLED"
                    for z in s.get("zoneSets", [])
                )
            )

    run(body())


def test_duplicate_zone_set_rejected_original_kept():
    async def body():
        async with Stack() as stack:
            original = zone_set("zs-dup", [rect_zone("z1", "BLOCKED", 90, 91)])
            await stack.m.send_zone_set(original)
            await stack.m.next_state(
                lambda s: any(z["zoneSetId"] == "zs-dup" for z in s.get("zoneSets", []))
            )
            await stack.m.send_zone_set(zone_set("zs-dup", [rect_zone("z2", "BLOCKED", 5, 6)]))
            error = await await_error(stack, "DUPLICATE_ZONE_SET")
            assert error["errorLevel"] == "WARNING"
            assert stack.r.zones.zone_sets["zs-dup"].zones[0]["zoneId"] == "z1"

    run(body())


def test_unsupported_zone_type_rejected():
    async def body():
        async with Stack() as stack:
            # Note: the official 3.0.0 schema calls the DIRECTED parameter
            # `limitation` (the PDF table says `directedLimitation`).
            bad = zone_set(
                "zs-directed",
                [rect_zone("zd", "DIRECTED", 1, 2, direction=0.0, limitation="SOFT")],
            )
            await stack.m.send_zone_set(bad)
            await await_error(stack, "VALIDATION_FAILURE")
            assert "zs-directed" not in stack.r.zones.zone_sets

    run(body())


def test_enable_unknown_zone_set_fails():
    async def body():
        async with Stack() as stack:
            action = await stack.m.send_instant_action(
                "enableZoneSet", parameters={"zoneSetId": "missing"}
            )
            final = await stack.m.action_status(action, statuses=("FINISHED", "FAILED"))
            assert final["actionStatus"] == "FAILED"

    run(body())


def test_release_zone_gates_until_granted_then_request_removed_after_exit():
    async def body():
        async with Stack() as stack:
            await stack.m.send_zone_set(
                zone_set("zs-rel", [rect_zone("z-gate", "RELEASE", 1.4, 2.6)])
            )
            await enable(stack, "zs-rel")
            nodes, edges = straight_order(n=4)
            await stack.m.send_order(nodes, edges, order_id="o-rel")
            state = await stack.m.next_state(
                lambda s: any(r["requestStatus"] == "REQUESTED" for r in s.get("zoneRequests", [])),
                timeout=15,
            )
            request = state["zoneRequests"][0]
            assert request["requestType"] == "ACCESS"
            assert request["zoneId"] == "z-gate"
            assert request["zoneSetId"] == "zs-rel"
            # Unanswered: 10 simulated seconds pass, the robot must not move on.
            await asyncio.sleep(0.05)
            latest = stack.m.states[-1]
            assert latest["lastNodeId"] == "n1"
            assert latest["driving"] is False
            await stack.m.respond(request["requestId"], "GRANTED")
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n3" and not s["nodeStates"], timeout=15
            )
            # Robot exited the zone on the way to n3 -> request dropped.
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n3" and not s.get("zoneRequests", []),
                timeout=15,
            )
            assert state["errors"] == []

    run(body())


def test_release_zone_rejected_keeps_robot_stopped():
    async def body():
        async with Stack() as stack:
            await stack.m.send_zone_set(
                zone_set("zs-rej", [rect_zone("z-no", "RELEASE", 1.4, 2.6)])
            )
            await enable(stack, "zs-rej")
            nodes, edges = straight_order(n=3)
            await stack.m.send_order(nodes, edges, order_id="o-rej")
            state = await stack.m.next_state(
                lambda s: any(r["requestStatus"] == "REQUESTED" for r in s.get("zoneRequests", [])),
                timeout=15,
            )
            request = state["zoneRequests"][0]
            await stack.m.respond(request["requestId"], "REJECTED")
            await asyncio.sleep(0.05)  # 10 simulated seconds
            latest = stack.m.states[-1]
            assert latest["lastNodeId"] == "n1"
            assert latest["driving"] is False
            assert latest["zoneRequests"][0]["requestStatus"] == "REQUESTED"

    run(body())


def test_release_revoked_while_inside_reports_release_lost():
    async def body():
        async with Stack(scale=20.0) as stack:
            await stack.m.send_zone_set(
                zone_set("zs-rev", [rect_zone("z-rev", "RELEASE", 1.4, 4.6)])
            )
            await enable(stack, "zs-rev")
            nodes, edges = straight_order(n=6)
            await stack.m.send_order(nodes, edges, order_id="o-rev")
            state = await stack.m.next_state(
                lambda s: any(r["requestStatus"] == "REQUESTED" for r in s.get("zoneRequests", [])),
                timeout=15,
            )
            request = state["zoneRequests"][0]
            await stack.m.respond(request["requestId"], "GRANTED")
            # Freeze the robot while it is inside the zone, then revoke.
            await stack.m.next_state(lambda s: s["lastNodeId"] == "n2", timeout=15)
            pause = await stack.m.send_instant_action("startPause")
            await stack.m.action_status(pause, statuses=("FINISHED",))
            await stack.m.respond(request["requestId"], "REVOKED")
            await stack.m.next_state(
                lambda s: any(r["requestStatus"] == "REVOKED" for r in s.get("zoneRequests", [])),
                timeout=15,
            )
            resume = await stack.m.send_instant_action("stopPause")
            await stack.m.action_status(resume, statuses=("FINISHED",))
            # 6.4.3: release revoked while inside the zone, default
            # releaseLossBehavior STOP -> the robot stops and reports
            # RELEASE_LOST with level CRITICAL.
            error = await await_error(stack, "RELEASE_LOST", timeout=15)
            assert error["errorLevel"] == "CRITICAL"
            latest = stack.m.states[-1]
            assert latest["driving"] is False
            assert latest["zoneRequests"][0]["requestStatus"] == "REVOKED"

    run(body())


def test_blocked_zone_stops_robot_before_entry():
    async def body():
        async with Stack() as stack:
            await stack.m.send_zone_set(
                zone_set("zs-blk", [rect_zone("z-blk", "BLOCKED", 1.4, 2.6)])
            )
            await enable(stack, "zs-blk")
            nodes, edges = straight_order(n=3)
            await stack.m.send_order(nodes, edges, order_id="o-blk")
            error = await await_error(stack, "NODE_UNREACHABLE", timeout=15)
            assert error["errorLevel"] == "CRITICAL"
            await asyncio.sleep(0.05)
            latest = stack.m.states[-1]
            assert latest["mobileRobotPosition"]["x"] <= 1.45
            assert latest["driving"] is False
            assert latest["lastNodeId"] == "n1"

    run(body())


def test_speed_limit_zone_slows_covered_edge():
    async def body():
        # Low time scale on purpose: the assertion compares simulated
        # durations, and at high scales a few milliseconds of event-loop lag
        # on a busy CI runner inflates simulated time enough to drown the
        # speed-limit signal.
        async with Stack(scale=20.0) as stack:
            await stack.m.send_zone_set(
                zone_set(
                    "zs-slow",
                    [rect_zone("z-slow", "SPEED_LIMIT", 1.1, 1.9, maximumSpeed=0.25)],
                )
            )
            await enable(stack, "zs-slow")
            nodes, edges = straight_order(n=3)
            await stack.m.send_order(nodes, edges, order_id="o-slow")
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=20
            )
            at_n1 = await stack.m.next_state(lambda s: s["lastNodeId"] == "n1")
            at_n2 = await stack.m.next_state(lambda s: s["lastNodeId"] == "n2")
            accepted = await stack.m.next_state(
                lambda s: s["orderId"] == "o-slow" and s["lastNodeId"] == "n0"
            )
            uncovered = sim_ts(at_n1) - sim_ts(accepted)  # n0 -> n1, no zone
            covered = sim_ts(at_n2) - sim_ts(at_n1)  # n1 -> n2, 0.8 m at 0.25 m/s
            assert covered > 1.5 * uncovered, (covered, uncovered)

    run(body())


def test_action_zone_runs_entry_actions_and_clear():
    async def body():
        async with Stack() as stack:
            await stack.m.send_zone_set(
                zone_set(
                    "zs-act",
                    [
                        rect_zone(
                            "z-act",
                            "ACTION",
                            0.4,
                            1.6,
                            entryActions=[{"actionType": "detectObject", "blockingType": "NONE"}],
                            duringActions=[],
                            exitActions=[],
                        )
                    ],
                )
            )
            await enable(stack, "zs-act")
            nodes, edges = straight_order(n=3)
            await stack.m.send_order(nodes, edges, order_id="o-act")
            state = await stack.m.next_state(
                lambda s: any(
                    a.get("actionType") == "detectObject" and a["actionStatus"] == "FINISHED"
                    for a in s.get("zoneActionStates", [])
                ),
                timeout=20,
            )
            assert state["zoneActionStates"]
            clear = await stack.m.send_instant_action("clearZoneActions")
            await stack.m.action_status(clear, statuses=("FINISHED",))
            await stack.m.next_state(lambda s: s.get("zoneActionStates") == [], timeout=10)

    run(body())


def test_invalid_zone_set_message_reports_validation_failure():
    async def body():
        async with Stack() as stack:
            await stack.m.publish_raw(
                "zoneSet", {"zoneSet": {"zoneSetId": "zs-bad", "mapId": "map-0"}}
            )
            await await_error(stack, "VALIDATION_FAILURE")
            assert "zs-bad" not in stack.r.zones.zone_sets
            # Robot still fully operational afterwards.
            nodes, edges = straight_order(n=2)
            await stack.m.send_order(nodes, edges, order_id="o-after")
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n1" and not s["nodeStates"], timeout=15
            )

    run(body())
