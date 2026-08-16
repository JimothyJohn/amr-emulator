"""End-to-end: VDA 5050 master -> adapter -> MiR emulator (in-process ASGI).

The MiR side is the real mir-emulator app (3.8.1) mounted over httpx's ASGI
transport — full REST semantics, mission simulation and pose interpolation,
no TCP needed. The VDA side is the vda5050-emulator's broker + MasterControl.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest
from mir_emulator import create_app
from mir_vda5050_adapter import AdapterConfig, MiRVDA5050Adapter
from vda5050_emulator import Broker, MasterControl, make_action, make_edge, make_node
from vda5050_emulator.validation import validation_errors

TIMEOUT = 60.0


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, TIMEOUT))


class Stack:
    def __init__(self, version: str = "2.0.0") -> None:
        self.version = version

    async def __aenter__(self):
        self.mir_app = create_app("3.8.1", mission_duration=3.0)
        self.broker = Broker(port=0)
        await self.broker.start()
        self.adapter = MiRVDA5050Adapter(
            AdapterConfig(
                version=self.version,
                poll_interval=0.05,
                min_state_interval=0.01,
                state_interval=1.0,
            ),
            port=self.broker.port,
            mir_transport=httpx.ASGITransport(app=self.mir_app),
        )
        await self.adapter.start()
        self.master = MasterControl(
            "127.0.0.1",
            self.broker.port,
            manufacturer=self.adapter.topics.manufacturer,
            serial_number=self.adapter.topics.serial_number,
            version=self.version,
        )
        await self.master.connect()
        await self.master.next_state(timeout=10)
        return self

    async def __aexit__(self, *exc):
        await self.master.disconnect()
        await self.adapter.stop()
        await self.broker.stop()

    def order(self, order_id: str = "o-1", n: int = 3):
        # The MiR emulator starts at (5, 5); first node = current position.
        x0, y0 = self.adapter.x, self.adapter.y
        nodes = [
            make_node(
                f"n{i}",
                2 * i,
                x=x0 + 0.9 * i,
                y=y0,
                theta=0.0,
                map_id=self.adapter.map_id,
                version=self.version,
            )
            for i in range(n)
        ]
        edges = [
            make_edge(
                f"e{i}",
                2 * i + 1,
                start_node_id=f"n{i}",
                end_node_id=f"n{i + 1}",
                version=self.version,
            )
            for i in range(n - 1)
        ]
        return nodes, edges


def test_order_executes_on_mir_and_completes():
    async def body():
        async with Stack() as stack:
            nodes, edges = stack.order()
            await stack.master.send_order(nodes, edges, order_id="o-1")
            state = await stack.master.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=45
            )
            assert state["orderId"] == "o-1"
            assert not state["errors"]
            # The MiR emulator really moved: adapter's pose came from /status.
            assert abs(state["agvPosition"]["x"] - (5.0 + 1.8)) < 0.5
            for doc in stack.master.states:
                assert not validation_errors("state", doc, tag="2.0.0")

    run(body())


def test_order_with_node_actions_rejected():
    async def body():
        async with Stack() as stack:
            nodes, edges = stack.order(order_id="o-act")
            nodes[1]["actions"] = [make_action("pick")]
            await stack.master.send_order(nodes, edges, order_id="o-act")
            state = await stack.master.next_state(
                lambda s: any(e["errorType"] == "orderError" for e in s["errors"]),
                timeout=30,
            )
            assert state["orderId"] == ""  # never accepted

    run(body())


def test_cancel_order_clears_mir_queue():
    async def body():
        async with Stack() as stack:
            nodes, edges = stack.order(order_id="o-cancel", n=3)
            await stack.master.send_order(nodes, edges, order_id="o-cancel")
            await stack.master.next_state(lambda s: s["driving"], timeout=30)
            aid = await stack.master.send_instant_action("cancelOrder")
            await stack.master.action_status(aid, statuses=("FINISHED",), timeout=15)
            state = await stack.master.next_state(
                lambda s: s["orderId"] == "o-cancel" and not s["nodeStates"] and not s["driving"],
                timeout=20,
            )
            assert state["orderId"] == "o-cancel"  # ids kept per 6.1.3
            # New order accepted afterwards (fresh orderId).
            nodes2, edges2 = stack.order(order_id="o-next", n=2)
            await stack.master.send_order(nodes2, edges2, order_id="o-next")
            await stack.master.next_state(lambda s: s["orderId"] == "o-next", timeout=15)

    run(body())


def test_pause_and_resume_via_mir_state():
    async def body():
        async with Stack() as stack:
            nodes, edges = stack.order(order_id="o-pause", n=3)
            await stack.master.send_order(nodes, edges, order_id="o-pause")
            await stack.master.next_state(lambda s: s["driving"], timeout=30)
            pause = await stack.master.send_instant_action("startPause")
            await stack.master.action_status(pause, statuses=("FINISHED",), timeout=15)
            await stack.master.next_state(lambda s: s.get("paused") is True, timeout=15)
            resume = await stack.master.send_instant_action("stopPause")
            await stack.master.action_status(resume, statuses=("FINISHED",), timeout=15)
            await stack.master.next_state(
                lambda s: s["lastNodeId"] == "n2" and not s["nodeStates"], timeout=45
            )

    run(body())


def test_factsheet_advertises_only_supported_actions():
    async def body():
        async with Stack() as stack:
            aid = await stack.master.send_instant_action("factsheetRequest")
            await stack.master.action_status(aid, statuses=("FINISHED",), timeout=15)
            for _ in range(100):
                if stack.master.factsheets:
                    break
                await asyncio.sleep(0.05)
            sheet = stack.master.factsheets[-1]
            assert not validation_errors("factsheet", sheet, tag="2.0.0")
            advertised = {a["actionType"] for a in sheet["protocolFeatures"]["agvActions"]}
            # 2.0.0 has no factsheetRequest in its predefined action table, so
            # the factsheet (filtered by the profile) must not advertise it —
            # the adapter still answers it for compatibility.
            assert advertised == {"cancelOrder", "startPause", "stopPause", "stateRequest"}

    run(body())


def test_unsupported_instant_action_fails_cleanly():
    async def body():
        async with Stack() as stack:
            aid = await stack.master.send_instant_action("startCharging")
            entry = await stack.master.action_status(aid, statuses=("FAILED",), timeout=15)
            assert entry["actionStatus"] == "FAILED"

    run(body())


@pytest.mark.parametrize("version", ("2.1.0", "3.0.0"))
def test_other_profiles_publish_valid_state(version):
    async def body():
        async with Stack(version) as stack:
            nodes, edges = stack.order(order_id="o-v", n=2)
            await stack.master.send_order(nodes, edges, order_id="o-v")
            await stack.master.next_state(
                lambda s: s["lastNodeId"] == "n1" and not s["nodeStates"], timeout=45
            )
            for doc in stack.master.states:
                assert not validation_errors("state", doc, tag=version)

    run(body())
