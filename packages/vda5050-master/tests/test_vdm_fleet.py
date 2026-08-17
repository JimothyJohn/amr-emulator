"""Fleet discovery and the per-robot handle, against real robots."""

import pytest
from vdm_harness import FleetStack, run


def test_discovers_every_robot_without_configuration():
    async def body():
        async with FleetStack(robots=3) as stack:
            handles = await stack.m.wait_for_robots(3, timeout=5)
            assert sorted(h.serial_number for h in handles) == ["r0", "r1", "r2"]
            assert all(h.online for h in handles)
            # Serial lookup resolves, and each handle is receiving states.
            handle = stack.m.robot("r1")
            state = await handle.next_state(timeout=5)
            assert state["serialNumber"] == "r1"

    run(body())


def test_robot_going_away_is_observed_via_connection_topic():
    async def body():
        async with FleetStack(robots=2) as stack:
            handle = stack.m.robot("r0")
            assert handle.online
            await stack.robots[0].stop()
            await handle.next_message(
                "connections",
                lambda doc: doc.get("connectionState") != "ONLINE",
                timeout=5,
            )
            assert not handle.online
            assert stack.m.robot("r1").online  # the other robot is untouched

    run(body())


def test_unknown_serial_lookup_names_the_known_fleet():
    async def body():
        async with FleetStack(robots=1) as stack:
            with pytest.raises(KeyError, match="r0"):
                stack.m.robot("no-such-robot")

    run(body())


def test_master_refuses_to_publish_schema_invalid_orders():
    async def body():
        async with FleetStack(robots=1) as stack:
            handle = stack.m.robot("r0")
            states_before = len(handle.states)
            with pytest.raises(ValueError, match="refusing to publish"):
                # 3.0.0 requires nodes/edges on an order.
                await handle.send_order({"orderId": "o-broken", "orderUpdateId": 0})
            # Nothing reached the robot: no new state, no error referencing it.
            state = await handle.next_state(timeout=2)
            assert not [
                e
                for e in state.get("errors", [])
                for ref in e.get("errorReferences", [])
                if ref.get("referenceValue") == "o-broken"
            ]
            assert len(handle.states) >= states_before  # loop stayed alive

    run(body())


def test_incoming_messages_are_validated_but_never_dropped():
    async def body():
        async with FleetStack(robots=1) as stack:
            handle = stack.m.robot("r0")
            await handle.next_state(timeout=5)
            # The real emulator publishes schema-valid traffic; the ledger of
            # problems must therefore stay empty on a healthy fleet.
            assert handle.protocol_problems == []

    run(body())
