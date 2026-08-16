"""Action engine semantics: the blocking rules of Figure 11, the state
transitions of Tables 5/12/13, pausing, triggering, and the predefined
map/charging/log actions."""

from __future__ import annotations

from vda_harness import Stack, run, straight_order
from vda5050_emulator import make_action


def _stamp(state: dict) -> str:
    return state["timestamp"]


def test_none_action_runs_while_driving():
    async def body():
        async with Stack() as stack:
            beep = make_action("detectObject", blocking_type="NONE")
            nodes, edges = straight_order(n=3)
            nodes[1]["actions"] = [beep]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            # While the NONE action runs, the robot may keep driving: find a
            # state where the action is RUNNING and driving is true.
            state = await stack.m.next_state(
                lambda s: (
                    any(
                        a["actionId"] == beep["actionId"] and a["actionStatus"] == "RUNNING"
                        for a in s["actionStates"]
                    )
                    and s["driving"]
                ),
                timeout=20,
            )
            assert state["driving"] is True

    run(body())


def test_hard_action_stops_driving_until_finished():
    async def body():
        async with Stack() as stack:
            lift = make_action("pick", blocking_type="HARD")
            nodes, edges = straight_order(n=3)
            nodes[1]["actions"] = [lift]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            state = await stack.m.next_state(
                lambda s: any(
                    a["actionId"] == lift["actionId"]
                    and a["actionStatus"] in ("INITIALIZING", "RUNNING")
                    for a in s["actionStates"]
                ),
                timeout=20,
            )
            assert state["driving"] is False and state["lastNodeId"] == "n1"
            await stack.m.action_status(lift["actionId"], statuses=("FINISHED",), timeout=20)
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=20
            )
            assert any(load for load in state.get("loads", [])), "pick must produce a load"

    run(body())


def test_single_waits_for_parallel_batch():
    async def body():
        async with Stack(action_duration=1.0) as stack:
            first = make_action("detectObject", blocking_type="NONE")
            second = make_action("finePositioning", blocking_type="SINGLE")
            nodes, edges = straight_order(n=2)
            nodes[1]["actions"] = [first, second]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.action_status(second["actionId"], statuses=("FINISHED",), timeout=20)
            # SINGLE must not have been RUNNING while the NONE action was
            # unfinished: replay the state history and check for overlap.
            for state in stack.m.states:
                statuses = {a["actionId"]: a["actionStatus"] for a in state["actionStates"]}
                if statuses.get(second["actionId"]) == "RUNNING":
                    assert statuses.get(first["actionId"]) in ("FINISHED", "FAILED"), (
                        "SINGLE ran while parallel batch was active"
                    )

    run(body())


def test_pause_and_resume_with_pauseable_action():
    async def body():
        async with Stack(pick_duration=5.0) as stack:
            lift = make_action("pick", blocking_type="HARD")
            nodes, edges = straight_order(n=2)
            nodes[1]["actions"] = [lift]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.action_status(lift["actionId"], statuses=("RUNNING",), timeout=20)
            pause_id = await stack.m.send_instant_action("startPause")
            await stack.m.action_status(pause_id, statuses=("FINISHED",), timeout=10)
            await stack.m.next_state(lambda s: s.get("paused") is True, timeout=10)
            await stack.m.action_status(lift["actionId"], statuses=("PAUSED",), timeout=10)
            resume_id = await stack.m.send_instant_action("stopPause")
            await stack.m.action_status(resume_id, statuses=("FINISHED",), timeout=10)
            await stack.m.next_state(lambda s: s.get("paused") is False, timeout=10)
            await stack.m.action_status(lift["actionId"], statuses=("FINISHED",), timeout=30)

    run(body())


def test_wait_for_trigger_and_trigger():
    async def body():
        async with Stack() as stack:
            wait = make_action(
                "waitForTrigger",
                blocking_type="HARD",
                parameters={"triggerType": ["FLEET_CONTROL"]},
            )
            nodes, edges = straight_order(n=2)
            nodes[1]["actions"] = [wait]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.action_status(wait["actionId"], statuses=("RUNNING",), timeout=20)
            trigger_id = await stack.m.send_instant_action("trigger")
            await stack.m.action_status(trigger_id, statuses=("FINISHED",), timeout=10)
            await stack.m.action_status(wait["actionId"], statuses=("FINISHED",), timeout=10)

    run(body())


def test_edge_actions_finish_on_node_traversal():
    async def body():
        async with Stack() as stack:
            hum = make_action("detectObject", blocking_type="NONE")
            nodes, edges = straight_order(n=2)
            edges[0]["actions"] = [hum]
            # Make the action outlast the edge so traversal has to finish it.
            hum["actionParameters"] = [{"key": "objectType", "value": "pallet"}]
            stack_config_duration = 60.0
            stack.r.config.action_duration = stack_config_duration
            await stack.m.send_order(nodes, edges, order_id="o-1")
            state = await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n1" and not s["edgeStates"], timeout=20
            )
            entry = next(a for a in state["actionStates"] if a["actionId"] == hum["actionId"])
            assert entry["actionStatus"] == "FINISHED", (
                "edge actions are finished when the edge is left (6.6.2)"
            )

    run(body())


def test_retriable_retry_and_skip():
    async def body():
        async with Stack() as stack:
            stack.r.inject(action_failure={"actionType": "pick", "mode": "RETRIABLE"})
            lift = make_action("pick", blocking_type="HARD", retriable=True)
            nodes, edges = straight_order(n=2)
            nodes[1]["actions"] = [lift]
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.action_status(lift["actionId"], statuses=("RETRIABLE",), timeout=20)
            retry_id = await stack.m.send_instant_action(
                "retry", parameters={"actionId": lift["actionId"]}
            )
            await stack.m.action_status(retry_id, statuses=("FINISHED",), timeout=10)
            await stack.m.action_status(lift["actionId"], statuses=("FINISHED",), timeout=20)

    run(body())


def test_charging_actions_toggle_power_supply():
    async def body():
        async with Stack() as stack:
            start = await stack.m.send_instant_action("startCharging")
            await stack.m.action_status(start, statuses=("FINISHED",), timeout=10)
            await stack.m.next_state(lambda s: s["powerSupply"]["charging"] is True, timeout=10)
            stop = await stack.m.send_instant_action("stopCharging")
            await stack.m.action_status(stop, statuses=("FINISHED",), timeout=10)
            await stack.m.next_state(lambda s: s["powerSupply"]["charging"] is False, timeout=10)

    run(body())


def test_map_download_enable_delete_cycle():
    async def body():
        async with Stack() as stack:
            download = await stack.m.send_instant_action(
                "downloadMap",
                parameters={
                    "mapId": "map-1",
                    "mapVersion": "7",
                    "mapDownloadLink": "https://maps.example/map-1.tar",
                },
            )
            await stack.m.action_status(download, statuses=("FINISHED",), timeout=20)
            await stack.m.next_state(
                lambda s: any(
                    m["mapId"] == "map-1" and m["mapStatus"] == "DISABLED"
                    for m in s.get("maps", [])
                ),
                timeout=10,
            )
            # duplicate download -> DUPLICATE_MAP + FAILED
            duplicate = await stack.m.send_instant_action(
                "downloadMap",
                parameters={
                    "mapId": "map-1",
                    "mapVersion": "7",
                    "mapDownloadLink": "https://maps.example/map-1.tar",
                },
            )
            await stack.m.action_status(duplicate, statuses=("FAILED",), timeout=20)
            await stack.m.next_state(
                lambda s: any(e["errorType"] == "DUPLICATE_MAP" for e in s["errors"]),
                timeout=10,
            )
            enable = await stack.m.send_instant_action(
                "enableMap", parameters={"mapId": "map-1", "mapVersion": "7"}
            )
            await stack.m.action_status(enable, statuses=("FINISHED",), timeout=10)
            await stack.m.next_state(
                lambda s: any(
                    m["mapId"] == "map-1" and m["mapStatus"] == "ENABLED" for m in s.get("maps", [])
                ),
                timeout=10,
            )
            # deleting the ENABLED map must fail; the original stays
            delete = await stack.m.send_instant_action(
                "deleteMap", parameters={"mapId": "map-1", "mapVersion": "7"}
            )
            await stack.m.action_status(delete, statuses=("FAILED",), timeout=10)

    run(body())


def test_clear_instant_actions():
    async def body():
        async with Stack() as stack:
            for _ in range(3):
                aid = await stack.m.send_instant_action("stateRequest")
                await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)
            clear_id = await stack.m.send_instant_action("clearInstantActions")
            await stack.m.action_status(clear_id, statuses=("FINISHED",), timeout=10)
            state = await stack.m.next_state(
                lambda s: len(s.get("instantActionStates", [])) <= 1, timeout=10
            )
            remaining = [a["actionId"] for a in state["instantActionStates"]]
            assert remaining in ([], [clear_id])

    run(body())


def test_unknown_instant_action_reports_invalid():
    async def body():
        async with Stack() as stack:
            aid = await stack.m.send_instant_action("summonDragon")
            entry = await stack.m.action_status(aid, statuses=("FAILED",), timeout=10)
            assert entry["actionStatus"] == "FAILED"
            state = await stack.m.next_state(
                lambda s: any(e["errorType"] == "INVALID_INSTANT_ACTION" for e in s["errors"]),
                timeout=10,
            )
            error = next(e for e in state["errors"] if e["errorType"] == "INVALID_INSTANT_ACTION")
            refs = {
                r["referenceKey"]: r["referenceValue"] for r in error.get("errorReferences", [])
            }
            assert refs.get("actionId") == aid

    run(body())
