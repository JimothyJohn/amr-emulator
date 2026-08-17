"""Failure-injection torture for the adapter: in a factory the MiR side WILL
misbehave (reboots, proxy error pages, half-dead Wi-Fi), and the adapter must
degrade observably — errors on the wire, no silent zombies, full recovery when
the robot returns."""

from __future__ import annotations

import asyncio
import json
import math

import httpx
from mir_emulator import create_app
from mir_vda5050_adapter import AdapterConfig, MiRVDA5050Adapter
from vda5050_emulator import Broker, MasterControl, make_action, make_edge, make_node
from vda5050_emulator.validation import validation_errors

TIMEOUT = 60.0


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, TIMEOUT))


class FlakyMiR(httpx.AsyncBaseTransport):
    """Wraps the mir-emulator ASGI transport with switchable failure modes.

    mode: "ok" | "http503" | "timeout" | "garbage" | "malformed:<n>"
    fail_paths: when non-empty, only requests whose path contains one of the
    fragments fail; everything else passes through.
    """

    MALFORMED = (
        {"battery_percentage": "very high", "state_id": 3},
        {"position": {"x": "NaN", "y": "Infinity", "orientation": "-Infinity"}},
        {"position": None, "state_id": 999, "errors": "broken"},
        {"state_id": "??", "battery_percentage": None, "map_id": 7},
        [],
    )

    def __init__(self, app) -> None:
        self.inner = httpx.ASGITransport(app=app)
        self.mode = "ok"
        self.fail_paths: tuple[str, ...] = ()
        self.calls: list[str] = []

    def _applies(self, request: httpx.Request) -> bool:
        if self.mode == "ok":
            return False
        if not self.fail_paths:
            return True
        return any(fragment in request.url.path for fragment in self.fail_paths)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(f"{request.method} {request.url.path}")
        if self._applies(request):
            if self.mode == "http503":
                return httpx.Response(503, text="Service Unavailable")
            if self.mode == "timeout":
                raise httpx.ConnectTimeout("injected timeout", request=request)
            if self.mode == "garbage":
                return httpx.Response(200, text="<html>proxy error page</html>")
            if self.mode.startswith("malformed:"):
                index = int(self.mode.split(":", 1)[1])
                return httpx.Response(200, json=self.MALFORMED[index])
        return await self.inner.handle_async_request(request)


class Stack:
    def __init__(self, **config) -> None:
        config.setdefault("poll_interval", 0.05)
        config.setdefault("min_state_interval", 0.01)
        config.setdefault("state_interval", 1.0)
        self.config = AdapterConfig(**config)

    async def __aenter__(self):
        self.mir_app = create_app("3.8.1", mission_duration=2.0)
        self.flaky = FlakyMiR(self.mir_app)
        self.broker = Broker(port=0)
        await self.broker.start()
        self.adapter = MiRVDA5050Adapter(
            self.config, port=self.broker.port, mir_transport=self.flaky
        )
        await self.adapter.start()
        self.master = MasterControl(
            "127.0.0.1",
            self.broker.port,
            manufacturer=self.adapter.topics.manufacturer,
            serial_number=self.adapter.topics.serial_number,
            version=self.config.version,
        )
        await self.master.connect()
        await self.master.next_state(timeout=10)
        return self

    async def __aexit__(self, *exc):
        self.flaky.mode = "ok"  # let teardown talk to MiR again
        await self.master.disconnect()
        await self.adapter.stop()
        await self.broker.stop()

    def order(self, order_id: str, n: int = 3):
        x0, y0 = self.adapter.x, self.adapter.y
        nodes = [
            make_node(
                f"n{i}",
                2 * i,
                x=x0 + 0.9 * i,
                y=y0,
                theta=0.0,
                map_id=self.adapter.map_id,
                version="2.0.0",
            )
            for i in range(n)
        ]
        edges = [
            make_edge(
                f"e{i}", 2 * i + 1, start_node_id=f"n{i}", end_node_id=f"n{i + 1}", version="2.0.0"
            )
            for i in range(n - 1)
        ]
        return nodes, edges


def _has_error(state: dict, error_type: str, needle: str = "") -> bool:
    return any(
        e["errorType"] == error_type and needle in e.get("errorDescription", "")
        for e in state["errors"]
    )


def test_mir_dies_during_order_translation_then_recovers():
    async def body():
        async with Stack() as stack:
            # Positions/mission creation succeed; the final enqueue POST dies.
            stack.flaky.mode = "http503"
            stack.flaky.fail_paths = ("/mission_queue",)
            nodes, edges = stack.order("o-doomed")
            await stack.master.send_order(nodes, edges, order_id="o-doomed")
            state = await stack.master.next_state(
                lambda s: _has_error(s, "orderError", "order aborted"), timeout=15
            )
            assert state["orderId"] == "o-doomed"  # ids kept; execution aborted
            assert not state["nodeStates"] and not state["edgeStates"]
            # Zombie-order regression: a NEW order must be accepted and run.
            stack.flaky.mode = "ok"
            stack.flaky.fail_paths = ()
            nodes2, edges2 = stack.order("o-recovered", n=2)
            await stack.master.send_order(nodes2, edges2, order_id="o-recovered")
            state = await stack.master.next_state(
                lambda s: (
                    s["orderId"] == "o-recovered"
                    and s["lastNodeId"] == "n1"
                    and not s["nodeStates"]
                ),
                timeout=30,
            )
            assert not _has_error(state, "orderError", "order aborted")

    run(body())


def test_polling_outage_reports_and_clears_without_clobbering_rejections():
    async def body():
        async with Stack() as stack:
            # Seed a real rejection error (shares wire type "orderError").
            nodes, edges = stack.order("o-bad", n=2)
            nodes[1]["actions"] = [make_action("pick")]
            await stack.master.send_order(nodes, edges, order_id="o-bad")
            await stack.master.next_state(
                lambda s: _has_error(s, "orderError", "unsupported actions"), timeout=15
            )
            # Kill MiR: the unreachable error must appear ALONGSIDE it.
            stack.flaky.mode = "timeout"
            state = await stack.master.next_state(
                lambda s: _has_error(s, "orderError", "unreachable"), timeout=15
            )
            assert _has_error(state, "orderError", "unsupported actions")
            # Heal MiR: unreachable clears, the rejection survives (condition
            # key discrimination — second regression angle on the CI heisenbug).
            stack.flaky.mode = "ok"
            state = await stack.master.next_state(
                lambda s: (
                    not _has_error(s, "orderError", "unreachable")
                    and _has_error(s, "orderError", "unsupported actions")
                ),
                timeout=15,
            )
            assert state is not None

    run(body())


def test_mir_dies_during_cancel_order():
    async def body():
        async with Stack() as stack:
            nodes, edges = stack.order("o-cancel", n=3)
            await stack.master.send_order(nodes, edges, order_id="o-cancel")
            await stack.master.next_state(lambda s: s["driving"], timeout=30)
            stack.flaky.mode = "timeout"
            stack.flaky.fail_paths = ("/mission_queue",)  # DELETE fails; polls keep working
            aid = await stack.master.send_instant_action("cancelOrder")
            entry = await stack.master.action_status(aid, statuses=("FAILED",), timeout=15)
            assert "MiR API error" in entry.get("actionResult", "")

    run(body())


def test_malformed_status_documents_never_kill_polling_or_state_validity():
    async def body():
        async with Stack() as stack:
            baseline_battery = stack.adapter.battery
            for index in range(len(FlakyMiR.MALFORMED)):
                stack.flaky.mode = f"malformed:{index}"
                await asyncio.sleep(0.15)  # several polls per payload
            stack.flaky.mode = "garbage"  # 200 with non-JSON body
            await asyncio.sleep(0.15)
            stack.flaky.mode = "ok"
            # Poll loop must still be alive: battery resumes tracking MiR.
            await stack.master.send_instant_action("stateRequest")
            await stack.master.next_state(timeout=10)
            # Every published state remains schema-valid and finite.
            for doc in stack.master.states:
                assert not validation_errors("state", doc, tag="2.0.0")
                position = doc["agvPosition"]
                assert math.isfinite(position["x"]) and math.isfinite(position["y"])
                assert math.isfinite(position["theta"])
                assert 0.0 <= doc["batteryState"]["batteryCharge"] <= 100.0
            assert math.isfinite(stack.adapter.battery)
            assert abs(stack.adapter.battery - baseline_battery) < 50.0
            # And the adapter still executes orders afterwards.
            nodes, edges = stack.order("o-after-garbage", n=2)
            await stack.master.send_order(nodes, edges, order_id="o-after-garbage")
            await stack.master.next_state(
                lambda s: s["orderId"] == "o-after-garbage" and not s["nodeStates"], timeout=30
            )

    run(body())


def test_broker_death_does_not_spin_or_crash_the_adapter():
    async def body():
        async with Stack() as stack:
            nodes, edges = stack.order("o-broker", n=3)
            await stack.master.send_order(nodes, edges, order_id="o-broker")
            await stack.master.next_state(lambda s: s["driving"], timeout=30)
            await stack.broker.stop()
            # Give the adapter a moment on the dead connection.
            before = asyncio.get_running_loop().time()
            await asyncio.sleep(0.5)
            lag = asyncio.get_running_loop().time() - before - 0.5
            assert lag < 0.3, f"event loop starved ({lag:.3f}s lag): adapter busy-looping"
            for task in stack.adapter._tasks:
                assert not task.done(), "an adapter loop died on broker loss"
            # Documented behavior: no MQTT reconnect, but the MiR side keeps
            # operating — polling continues and the mission still tracks.
            assert stack.adapter.client.connected is False
            stack.flaky.calls.clear()
            await asyncio.sleep(0.3)
            assert any("/status" in call for call in stack.flaky.calls)

    run(body())


def test_update_before_base_then_base_recovers():
    async def body():
        async with Stack() as stack:
            nodes, edges = stack.order("o-order", n=2)
            update_first = json.loads(json.dumps(nodes))  # same shape, updateId 1
            await stack.master.send_order(
                update_first, edges, order_id="o-order", order_update_id=1
            )
            await stack.master.next_state(
                lambda s: _has_error(s, "validationError", "orderUpdateId 0"), timeout=15
            )
            await stack.master.send_order(nodes, edges, order_id="o-order", order_update_id=0)
            state = await stack.master.next_state(
                lambda s: s["orderId"] == "o-order" and not s["nodeStates"], timeout=30
            )
            assert not _has_error(state, "validationError", "orderUpdateId 0")

    run(body())


def test_state_publish_rate_is_bounded_under_touch_storm():
    async def body():
        async with Stack(poll_interval=0.01, min_state_interval=0.05) as stack:
            # Hammer the dirty flag far faster than the debounce.
            async def storm():
                for _ in range(400):
                    stack.adapter.touch()
                    await asyncio.sleep(0.005)

            loop = asyncio.get_running_loop()
            start = len(stack.master.states)
            t0 = loop.time()
            await storm()
            await asyncio.sleep(0.2)
            elapsed = loop.time() - t0
            observed = len(stack.master.states) - start
            # The invariant is SPACING (>= min_state_interval between
            # publishes), so the ceiling must derive from the observed
            # window: under CPU contention the storm's sleeps stretch and a
            # fixed ceiling flakes while the debounce is working perfectly.
            ceiling = elapsed / 0.05 * 1.15 + 2
            assert observed <= ceiling, (
                f"{observed} states in {elapsed:.2f}s (ceiling {ceiling:.0f}): "
                "debounce not bounding"
            )
            # Inbound loop was not starved by the storm.
            aid = await stack.master.send_instant_action("stateRequest")
            await stack.master.action_status(aid, statuses=("FINISHED",), timeout=10)

    run(body())


def test_twenty_concurrent_instant_actions_with_duplicates_and_unknowns():
    async def body():
        async with Stack() as stack:
            sends = []
            for i in range(10):
                sends.append(stack.master.send_instant_action("stateRequest", action_id=f"sr-{i}"))
            for _ in range(5):
                sends.append(stack.master.send_instant_action("stateRequest", action_id="dup-1"))
            for i in range(5):
                sends.append(stack.master.send_instant_action("summonDragon", action_id=f"bad-{i}"))
            await asyncio.gather(*sends)
            for i in range(10):
                await stack.master.action_status(f"sr-{i}", statuses=("FINISHED",), timeout=15)
            await stack.master.action_status("dup-1", statuses=("FINISHED",), timeout=15)
            for i in range(5):
                await stack.master.action_status(f"bad-{i}", statuses=("FAILED",), timeout=15)
            state = await stack.master.next_state(timeout=5)
            dup_entries = [a for a in state["actionStates"] if a["actionId"] == "dup-1"]
            assert len(dup_entries) == 1, "duplicate delivery created duplicate states"
            for doc in stack.master.states:
                assert not validation_errors("state", doc, tag="2.0.0")

    run(body())
