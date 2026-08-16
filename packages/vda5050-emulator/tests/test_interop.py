"""Interop and process-level integration.

The embedded broker is only worth anything if real MQTT stacks accept it, so
paho-mqtt (the ecosystem's canonical client) plays the master control here
over real TCP: subscribes with wildcards, receives the retained factsheet and
connection message, sends an order, and watches the robot drive. A second test
boots the actual ``vda5050-emulator`` CLI as a subprocess.
"""

from __future__ import annotations

import asyncio
import json
import queue
import re
import subprocess
import sys
import time
import uuid

import paho.mqtt.client as paho
import pytest
from vda_harness import Stack, run, straight_order

pytestmark = pytest.mark.integration


def _paho_connect(port: int, topics: list[str]) -> tuple[paho.Client, queue.Queue]:
    inbox: queue.Queue = queue.Queue()
    client = paho.Client(
        callback_api_version=paho.CallbackAPIVersion.VERSION2,
        client_id=f"paho-{uuid.uuid4().hex[:6]}",
        protocol=paho.MQTTv311,
    )
    client.on_message = lambda _c, _u, msg: inbox.put(msg)
    client.connect("127.0.0.1", port)
    for topic in topics:
        client.subscribe(topic)
    client.loop_start()
    return client, inbox


def _drain_until(inbox: queue.Queue, predicate, timeout: float = 15.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            msg = inbox.get(timeout=max(0.05, deadline - time.monotonic()))
        except queue.Empty:
            break
        if predicate(msg):
            return msg
    raise AssertionError("paho client did not receive the expected message")


def test_paho_master_control_drives_the_robot():
    async def body():
        async with Stack() as stack:
            prefix = stack.r.topics.prefix
            loop = asyncio.get_running_loop()

            def paho_session():
                client, inbox = _paho_connect(stack.port, [f"{prefix.rsplit('/', 2)[0]}/+/+/#"])
                try:
                    # Retained messages arrive on subscribe: factsheet + connection.
                    _drain_until(
                        inbox,
                        lambda m: (
                            m.topic.endswith("/connection")
                            and json.loads(m.payload)["connectionState"] == "ONLINE"
                        ),
                    )
                    _drain_until(inbox, lambda m: m.topic.endswith("/factsheet"))
                    nodes, edges = straight_order(n=2)
                    order = {
                        "headerId": 0,
                        "timestamp": "2026-01-01T00:00:00.000Z",
                        "version": "3.0.0",
                        "manufacturer": stack.r.topics.manufacturer,
                        "serialNumber": stack.r.topics.serial_number,
                        "orderId": "o-paho",
                        "orderUpdateId": 0,
                        "nodes": nodes,
                        "edges": edges,
                    }
                    info = client.publish(f"{prefix}/order", json.dumps(order).encode())
                    info.wait_for_publish(timeout=5)
                    done = _drain_until(
                        inbox,
                        lambda m: (
                            m.topic.endswith("/state")
                            and json.loads(m.payload).get("lastNodeId") == "n1"
                            and not json.loads(m.payload)["nodeStates"]
                        ),
                    )
                    return json.loads(done.payload)
                finally:
                    client.loop_stop()
                    client.disconnect()

            final_state = await loop.run_in_executor(None, paho_session)
            assert final_state["orderId"] == "o-paho"

    run(body(), timeout=60)


def test_cli_subprocess_end_to_end():
    process = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "vda5050_emulator.cli",
            "--port",
            "0",
            "--time-scale",
            "50",
            "--robots",
            "2",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        assert process.stdout is not None
        banner = ""
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            line = process.stdout.readline()
            banner += line
            if "five-minute check" in line:
                break
        match = re.search(r"mqtt://[\w.]+:(\d+)", banner)
        assert match, banner
        port = int(match.group(1))
        assert "vagv-0001" in banner and "vagv-0002" in banner

        client, inbox = _paho_connect(port, ["vda5050/v3/+/+/state"])
        try:
            seen: set[str] = set()

            def two_robots(msg) -> bool:
                seen.add(json.loads(msg.payload)["serialNumber"])
                return len(seen) >= 2

            _drain_until(inbox, two_robots, timeout=40)
        finally:
            client.loop_stop()
            client.disconnect()
    finally:
        process.terminate()
        process.wait(timeout=10)
