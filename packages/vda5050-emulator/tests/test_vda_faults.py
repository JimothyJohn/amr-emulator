"""Fault injection: the `_emulator` control topic and the Python inject() API.

Everything here is emulator-specific (not VDA 5050), but the observable
consequences — safetyState, errors, operating modes, RETRIABLE cycles,
CONNECTION_BROKEN wills — are exactly what a master control implementer needs
to harden against, so the tests double as documentation of the fault surface.
"""

from __future__ import annotations

import asyncio

from vda_harness import Stack, await_error, run, straight_order
from vda5050_emulator import make_action, make_edge, make_node


async def wait_connection(stack: Stack, value: str, timeout: float = 5.0) -> None:
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        if any(c.get("connectionState") == value for c in stack.m.connections):
            return
        await asyncio.sleep(0.01)
    raise TimeoutError(f"never saw connectionState {value}")


def test_emergency_stop_halts_and_clearing_resumes():
    async def body():
        async with Stack(scale=20.0) as stack:
            nodes, edges = straight_order(n=5)
            await stack.m.send_order(nodes, edges, order_id="o-estop")
            await stack.m.next_state(lambda s: s["driving"], timeout=15)
            stack.r.inject(emergency_stop="MANUAL")
            state = await stack.m.next_state(
                lambda s: s["safetyState"]["activeEmergencyStop"] == "MANUAL" and not s["driving"],
                timeout=15,
            )
            assert state["safetyState"]["fieldViolation"] is False
            stack.r.inject(emergency_stop="NONE")
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n4" and not s["nodeStates"], timeout=20
            )
            assert state["safetyState"]["activeEmergencyStop"] == "NONE"

    run(body())


def test_field_violation_blocks_driving():
    async def body():
        async with Stack(scale=20.0) as stack:
            nodes, edges = straight_order(n=5)
            await stack.m.send_order(nodes, edges, order_id="o-field")
            await stack.m.next_state(lambda s: s["driving"], timeout=15)
            stack.r.inject(field_violation=True)
            await stack.m.next_state(
                lambda s: s["safetyState"]["fieldViolation"] and not s["driving"],
                timeout=15,
            )
            stack.r.inject(field_violation=False)
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n4" and not s["nodeStates"], timeout=20
            )

    run(body())


def test_localization_loss_is_fatal_and_recoverable():
    async def body():
        async with Stack() as stack:
            stack.r.inject(localized=False)
            error = await await_error(stack, "LOCALIZATION_ERROR")
            assert error["errorLevel"] == "FATAL"
            nodes, edges = straight_order(n=2)
            await stack.m.send_order(nodes, edges, order_id="o-lost")
            await await_error(stack, "MOBILE_ROBOT_NOT_AVAILABLE")
            stack.r.inject(localized=True)
            await stack.m.next_state(
                lambda s: not any(e["errorType"] == "LOCALIZATION_ERROR" for e in s["errors"]),
                timeout=10,
            )
            await stack.m.send_order(nodes, edges, order_id="o-found")
            await stack.m.next_state(
                lambda s: (
                    s["orderId"] == "o-found" and s["lastNodeId"] == "n1" and not s["nodeStates"]
                ),
                timeout=15,
            )

    run(body())


def test_battery_override_via_emulator_topic():
    async def body():
        async with Stack() as stack:
            await stack.m.publish_raw("_emulator", {"battery": {"level": 7.0, "charging": True}})
            state = await stack.m.next_state(
                lambda s: s["powerSupply"]["charging"] is True, timeout=10
            )
            assert state["powerSupply"]["stateOfCharge"] <= 8.0

    run(body())


def test_teleport_via_emulator_topic():
    async def body():
        async with Stack() as stack:
            await stack.m.publish_raw("_emulator", {"teleport": {"x": 42.0, "y": -3.0}})
            state = await stack.m.next_state(
                lambda s: s["mobileRobotPosition"]["x"] == 42.0, timeout=10
            )
            assert state["mobileRobotPosition"]["y"] == -3.0

    run(body())


def test_manual_mode_clears_order_and_recovers():
    async def body():
        async with Stack(scale=20.0) as stack:
            wait = make_action(
                "waitForTrigger",
                blocking_type="HARD",
                parameters={"triggerType": ["FLEET_CONTROL"]},
            )
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0),
                make_node("n1", 2, x=1.0, y=0.0, actions=[wait]),
                make_node("n2", 4, x=2.0, y=0.0),
            ]
            edges = [make_edge("e0", 1), make_edge("e1", 3)]
            await stack.m.send_order(nodes, edges, order_id="o-manual")
            await stack.m.action_status(wait["actionId"], statuses=("RUNNING",), timeout=15)
            await stack.m.publish_raw("_emulator", {"operatingMode": "MANUAL"})
            state = await stack.m.next_state(lambda s: s["operatingMode"] == "MANUAL", timeout=10)
            assert state["nodeStates"] == [] and state["edgeStates"] == []
            assert state["lastNodeId"] == ""
            assert state["orderId"] == "o-manual"
            assert all(a["actionStatus"] in ("FINISHED", "FAILED") for a in state["actionStates"])
            await stack.m.publish_raw("_emulator", {"operatingMode": "AUTOMATIC"})
            await stack.m.next_state(lambda s: s["operatingMode"] == "AUTOMATIC", timeout=10)
            recovery = [make_node("r0", 0, x=0.0, y=0.0, deviation=50.0)]
            await stack.m.send_order(recovery, [], order_id="o-recovered")
            await stack.m.next_state(
                lambda s: s["orderId"] == "o-recovered" and s["lastNodeId"] == "r0",
                timeout=10,
            )

    run(body())


def test_forced_retriable_failure_then_retry_succeeds():
    async def body():
        async with Stack(scale=100.0) as stack:
            await stack.m.publish_raw(
                "_emulator", {"actionFailure": {"actionType": "pick", "mode": "RETRIABLE"}}
            )
            await asyncio.sleep(0.02)  # let the injection land before the order
            pick = make_action("pick", blocking_type="HARD", retriable=True)
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0),
                make_node("n1", 2, x=1.0, y=0.0, actions=[pick]),
            ]
            await stack.m.send_order(nodes, [make_edge("e0", 1)], order_id="o-retry")
            await stack.m.action_status(pick["actionId"], statuses=("RETRIABLE",), timeout=15)
            retry = await stack.m.send_instant_action(
                "retry", parameters={"actionId": pick["actionId"]}
            )
            await stack.m.action_status(retry, statuses=("FINISHED",), timeout=15)
            final = await stack.m.action_status(
                pick["actionId"], statuses=("FINISHED",), timeout=15
            )
            assert final["actionStatus"] == "FINISHED"

    run(body())


def test_forced_retriable_failure_then_skip_retry_fails():
    async def body():
        async with Stack(scale=100.0) as stack:
            stack.r.inject(action_failure={"actionType": "drop", "mode": "RETRIABLE"})
            drop = make_action("drop", blocking_type="HARD", retriable=True)
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0),
                make_node("n1", 2, x=1.0, y=0.0, actions=[drop]),
            ]
            await stack.m.send_order(nodes, [make_edge("e0", 1)], order_id="o-skip")
            await stack.m.action_status(drop["actionId"], statuses=("RETRIABLE",), timeout=15)
            skip = await stack.m.send_instant_action(
                "skipRetry", parameters={"actionId": drop["actionId"]}
            )
            await stack.m.action_status(skip, statuses=("FINISHED",), timeout=15)
            final = await stack.m.action_status(drop["actionId"], statuses=("FAILED",), timeout=15)
            assert final["actionStatus"] == "FAILED"

    run(body())


def test_disconnect_drop_publishes_connection_broken_will():
    async def body():
        async with Stack() as stack:
            await stack.m.publish_raw("_emulator", {"disconnect": "drop"})
            await wait_connection(stack, "CONNECTION_BROKEN")

    run(body())


def test_pause_pauses_pauseable_action_and_state_flags():
    async def body():
        async with Stack(scale=20.0) as stack:
            pick = make_action("pick", blocking_type="HARD")
            nodes = [
                make_node("n0", 0, x=0.0, y=0.0),
                make_node("n1", 2, x=1.0, y=0.0, actions=[pick]),
            ]
            await stack.m.send_order(nodes, [make_edge("e0", 1)], order_id="o-pause")
            await stack.m.action_status(pick["actionId"], statuses=("RUNNING",), timeout=15)
            start = await stack.m.send_instant_action("startPause")
            await stack.m.action_status(start, statuses=("FINISHED",))
            await stack.m.next_state(lambda s: s["paused"] and not s["driving"], timeout=10)
            await stack.m.action_status(pick["actionId"], statuses=("PAUSED",), timeout=15)
            stop = await stack.m.send_instant_action("stopPause")
            await stack.m.action_status(stop, statuses=("FINISHED",))
            await stack.m.next_state(lambda s: not s["paused"], timeout=10)
            final = await stack.m.action_status(
                pick["actionId"], statuses=("FINISHED",), timeout=20
            )
            assert final["actionStatus"] == "FINISHED"

    run(body())
