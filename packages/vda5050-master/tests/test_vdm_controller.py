"""Mission lifecycle against real robots: dispatch, progress, and every exit.

Covers the happy path on every supported protocol version plus the paths a
production fleet actually exercises: horizon extension, per-robot queuing,
multi-robot assignment, cancellation, rejection (with and without retry),
action failure surfaced, and a robot dying mid-mission.
"""

import pytest
from vda5050_emulator import supported_versions
from vda5050_master import Mission, MissionStatus, Waypoint, action
from vdm_harness import FleetStack, line_mission, run


@pytest.mark.parametrize("version", supported_versions())
def test_mission_completes_on_every_version(version):
    async def body():
        async with FleetStack(version=version) as stack:
            mission = line_mission(3)
            run_ = stack.c.submit(mission)
            assert await run_.wait(timeout=20) is MissionStatus.COMPLETED
            assert run_.final_state is not None
            assert run_.final_state["lastNodeId"] == mission.waypoints[-1].node_id
            assert run_.final_state["nodeStates"] == []

    run(body())


def test_horizon_extends_via_stitched_updates_until_done():
    async def body():
        async with FleetStack() as stack:
            mission = line_mission(4)
            run_ = stack.c.submit(mission, release=1)
            assert await run_.wait(timeout=25) is MissionStatus.COMPLETED
            handle = stack.m.robot("r0")
            final = [s for s in handle.states if s.get("orderId") == run_.order_id][-1]
            # 4 waypoints released one at a time -> 3 stitched updates.
            assert final["orderUpdateId"] == 3
            assert final["lastNodeId"] == mission.waypoints[-1].node_id

    run(body())


def test_one_robot_runs_missions_strictly_in_submission_order():
    async def body():
        async with FleetStack() as stack:
            first = stack.c.submit(line_mission(2, name="first"), robot="r0")
            second = stack.c.submit(line_mission(2, x0=1.0, name="second"), robot="r0")
            assert await second.wait(timeout=25) is MissionStatus.COMPLETED
            assert first.status is MissionStatus.COMPLETED
            handle = stack.m.robot("r0")
            order_ids = [s["orderId"] for s in handle.states if s.get("orderId")]
            # The robot never saw the second order before finishing the first.
            assert order_ids.index(second.order_id) > order_ids.index(first.order_id)

    run(body())


def test_assignment_spreads_missions_across_idle_robots():
    async def body():
        async with FleetStack(robots=2) as stack:
            runs = [stack.c.submit(line_mission(2, name=f"m{i}")) for i in range(2)]
            for run_ in runs:
                assert await run_.wait(timeout=25) is MissionStatus.COMPLETED
            assert {run_.robot_serial for run_ in runs} == {"r0", "r1"}

    run(body())


def test_cancel_mid_mission_stops_the_robot_and_reports_canceled():
    async def body():
        async with FleetStack() as stack:
            mission = line_mission(30, name="long")
            run_ = stack.c.submit(mission)
            handle = stack.m.robot("r0")
            # Let it genuinely start driving before pulling the plug.
            await handle.next_state(
                lambda s: (
                    s.get("orderId") == run_.order_id
                    and s.get("lastNodeId") not in ("", mission.waypoints[0].node_id)
                ),
                timeout=10,
            )
            await stack.c.cancel(run_)
            assert run_.status is MissionStatus.CANCELED
            state = await handle.next_state(
                lambda s: not s["nodeStates"] and not s["edgeStates"], timeout=10
            )
            assert state["lastNodeId"] != mission.waypoints[-1].node_id

    run(body())


def test_cancel_of_a_queued_mission_never_reaches_the_robot():
    async def body():
        async with FleetStack() as stack:
            blocker = stack.c.submit(line_mission(3, name="blocker"), robot="r0")
            queued = stack.c.submit(line_mission(3, name="queued"), robot="r0")
            await stack.c.cancel(queued)
            assert queued.status is MissionStatus.CANCELED
            assert await blocker.wait(timeout=25) is MissionStatus.COMPLETED
            handle = stack.m.robot("r0")
            assert not any(s.get("orderId") == queued.order_id for s in handle.states)

    run(body())


def test_rejected_order_fails_the_run_with_the_robots_errors():
    async def body():
        async with FleetStack() as stack:
            # First node far outside any deviation: START_NODE_OUT_OF_RANGE.
            unreachable = Mission([Waypoint(x=500.0, y=500.0)], name="far")
            run_ = stack.c.submit(unreachable)
            assert await run_.wait(timeout=15) is MissionStatus.FAILED
            assert "rejected" in run_.failure
            assert run_.errors, "the rejection error must be captured on the run"
            # Matching happened via errorReferences (2.x-safe), so the
            # captured error references the burned orderId.
            refs = {
                ref["referenceValue"]
                for error in run_.errors
                for ref in error.get("errorReferences", [])
                if ref.get("referenceKey") == "orderId"
            }
            assert run_.order_id in refs

    run(body())


def test_rejection_retry_burns_a_fresh_order_id_each_attempt():
    async def body():
        async with FleetStack() as stack:
            unreachable = Mission([Waypoint(x=500.0, y=500.0)], name="far")
            run_ = stack.c.submit(unreachable, retries=1)
            assert await run_.wait(timeout=15) is MissionStatus.FAILED
            order_ids = {
                ref["referenceValue"]
                for error in run_.errors
                for ref in error.get("errorReferences", [])
                if ref.get("referenceKey") == "orderId"
            }
            assert len(order_ids) == 2, "each attempt must use a fresh orderId"

    run(body())


@pytest.mark.parametrize("version", ["2.1.0", "3.0.0"])
def test_failed_mission_action_fails_the_run(version):
    # ``drop`` with nothing loaded fails deterministically. On 2.x that is a
    # straight FAILED; on 3.0 it surfaces as RETRIABLE, where the robot idles
    # until fleet control decides — the controller must skipRetry it so the
    # order settles, then fail the run. Either way: no silent limbo.
    async def body():
        async with FleetStack(version=version) as stack:
            futile = action("drop", blocking_type="HARD")
            mission = Mission(
                [Waypoint(x=0, y=0), Waypoint(x=1, y=0, actions=(futile,))], name="drop"
            )
            run_ = stack.c.submit(mission)
            assert await run_.wait(timeout=20) is MissionStatus.FAILED
            assert "actions failed" in run_.failure
            assert any(entry.get("actionId") == mission.action_ids[0] for entry in run_.errors)

    run(body())


def test_robot_dying_mid_mission_fails_the_run():
    async def body():
        async with FleetStack() as stack:
            mission = line_mission(30, name="doomed")
            run_ = stack.c.submit(mission)
            handle = stack.m.robot("r0")
            await handle.next_state(lambda s: s.get("orderId") == run_.order_id, timeout=10)
            await stack.robots[0].stop()
            assert await run_.wait(timeout=15) is MissionStatus.FAILED
            assert "mid-mission" in run_.failure

    run(body())


def test_submit_with_no_online_robots_raises_immediately():
    async def body():
        async with FleetStack() as stack:
            await stack.robots[0].stop()
            handle = stack.m.robot("r0")
            await handle.next_message(
                "connections",
                lambda doc: doc.get("connectionState") != "ONLINE",
                timeout=5,
            )
            with pytest.raises(LookupError, match="no online robots"):
                stack.c.submit(line_mission(2))

    run(body())
