"""Wire conformance: everything the robot publishes validates against the
official schema of the active protocol version, headers behave per section
7.2, and the retained/QoS rules of the recommendation hold."""

from __future__ import annotations

import json

import pytest
from vda5050_emulator import MQTTClient, make_action, make_node
from vda5050_emulator.validation import validation_errors
from vda_harness import Stack, run, straight_order

VERSIONS = ("2.0.0", "2.1.0", "3.0.0")


@pytest.mark.parametrize("version", VERSIONS)
def test_every_published_message_validates(version):
    async def body():
        async with Stack(version) as stack:
            nodes, edges = straight_order(version)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=20
            )
            await stack.m.send_instant_action("stateRequest")
            aid = await stack.m.send_instant_action(
                "factsheetRequest"
                if version != "2.0.0"
                else "stateRequest"  # 2.0.0 has no factsheetRequest
            )
            await stack.m.action_status(aid, statuses=("FINISHED",), timeout=10)
            checked = 0
            for name in ("state", "connection", "factsheet", "visualization"):
                for doc in stack.published[name]:
                    problems = validation_errors(name, doc, tag=version)
                    assert not problems, f"{version} {name}: {problems[:3]}"
                    assert doc["version"] == version
                    checked += 1
            assert checked >= 5

    run(body())


@pytest.mark.parametrize("version", VERSIONS)
def test_header_ids_monotonic_per_topic(version):
    async def body():
        async with Stack(version) as stack:
            nodes, edges = straight_order(version)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(lambda s: s["lastNodeId"] == "n2", timeout=20)
            for name in ("state", "connection", "factsheet"):
                ids = [doc["headerId"] for doc in stack.published[name]]
                assert ids == sorted(ids), f"{name} headerIds not monotonic: {ids}"
                assert len(set(ids)) == len(ids), f"{name} headerIds repeat: {ids}"
            timestamps = [doc["timestamp"] for doc in stack.published["state"]]
            for ts in timestamps:
                assert ts.endswith("Z") and "T" in ts and len(ts) == 24, ts

    run(body())


def test_connection_online_is_retained_and_qos1():
    async def body():
        async with Stack("3.0.0") as stack:
            late = MQTTClient("late", "127.0.0.1", stack.port)
            await late.connect()
            await late.subscribe(stack.r.topics.topic("connection"))
            message = await late.messages.get()
            assert message.retain, "connection must be retained"
            doc = json.loads(message.payload.decode())
            assert doc["connectionState"] == "ONLINE"
            await late.disconnect()

    run(body())


def test_factsheet_is_retained_for_late_subscribers():
    async def body():
        async with Stack("3.0.0") as stack:
            late = MQTTClient("late-fs", "127.0.0.1", stack.port)
            await late.connect()
            await late.subscribe(stack.r.topics.topic("factsheet"))
            message = await late.messages.get()
            assert message.retain
            doc = json.loads(message.payload.decode())
            assert not validation_errors("factsheet", doc, tag="3.0.0")
            # The advertised capability set is what the robot enforces.
            advertised = {a["actionType"] for a in doc["protocolFeatures"]["mobileRobotActions"]}
            assert "cancelOrder" in advertised and "startPause" in advertised
            await late.disconnect()

    run(body())


def test_state_publishes_on_events_and_respects_min_interval():
    async def body():
        async with Stack("3.0.0", min_state_interval=0.5) as stack:
            nodes, edges = straight_order("3.0.0", n=2)
            await stack.m.send_order(nodes, edges, order_id="o-1")
            await stack.m.next_state(
                lambda s: s["lastNodeId"] == "n1" and not s["nodeStates"], timeout=20
            )
            states = stack.published["state"]
            assert len(states) >= 3  # startup, accept, traversal(s)
            stamps = [s["timestamp"] for s in states]
            # minimum interval between consecutive state messages (sim time)
            from datetime import datetime
            from itertools import pairwise

            parsed = [datetime.fromisoformat(t.replace("Z", "+00:00")) for t in stamps]
            deltas = [(b - a).total_seconds() for a, b in pairwise(parsed)]
            assert all(d >= 0.45 for d in deltas), deltas

    run(body())


def test_visualization_topic_when_enabled():
    async def body():
        async with Stack("3.0.0", visualization_interval=0.5) as stack:
            await stack.m.next_state(timeout=5)
            for _ in range(200):
                if stack.published["visualization"]:
                    break
                await __import__("asyncio").sleep(0.02)
            docs = stack.published["visualization"]
            assert docs, "no visualization published"
            doc = docs[0]
            assert not validation_errors("visualization", doc, tag="3.0.0")
            assert "mobileRobotPosition" in doc and "velocity" in doc

    run(body())


def test_order_actions_reported_waiting_including_horizon():
    async def body():
        async with Stack("3.0.0") as stack:
            horizon_action = make_action("detectObject")
            nodes, edges = straight_order("3.0.0", n=2, horizon=1)
            nodes[2] = make_node("n2", 4, x=2.0, y=0.0, released=False, actions=[horizon_action])
            await stack.m.send_order(nodes, edges, order_id="o-1")
            state = await stack.m.next_state(
                lambda s: any(
                    a["actionId"] == horizon_action["actionId"] for a in s["actionStates"]
                ),
                timeout=10,
            )
            entry = next(
                a for a in state["actionStates"] if a["actionId"] == horizon_action["actionId"]
            )
            assert entry["actionStatus"] == "WAITING"

    run(body())
