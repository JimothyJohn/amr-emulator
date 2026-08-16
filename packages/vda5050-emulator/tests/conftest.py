"""Shared harness: one broker + one robot + one master, on fast simulated time.

The repo style runs async bodies through ``asyncio.run`` inside sync test
functions (no pytest-asyncio). ``run()`` adds a hard timeout so a deadlocked
robot fails the test instead of hanging the suite. ``Stack`` wires a fresh
embedded broker (ephemeral port), one ``VirtualAGV`` and one ``MasterControl``
plus a raw spy subscription capturing every message the robot publishes, so
conformance tests can validate the actual bytes on the wire.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections import defaultdict

from vda5050_emulator import AGVConfig, Broker, MasterControl, MQTTClient, VirtualAGV
from vda5050_emulator.clock import SimClock

TIMEOUT = 30.0


def run(coro, timeout: float = TIMEOUT):
    return asyncio.run(asyncio.wait_for(coro, timeout))


class Stack:
    def __init__(self, version: str = "3.0.0", *, scale: float = 200.0, **config) -> None:
        config.setdefault("visualization_interval", 0)
        self.config = AGVConfig(version=version, **config)
        self.version = version
        self.scale = scale
        self.broker: Broker | None = None
        self.robot: VirtualAGV | None = None
        self.master: MasterControl | None = None
        self.spy: MQTTClient | None = None
        self.published: dict[str, list[dict]] = defaultdict(list)
        self.raw_published: dict[str, list[bytes]] = defaultdict(list)
        self._spy_task: asyncio.Task | None = None

    async def __aenter__(self) -> Stack:
        self.broker = Broker(port=0)
        await self.broker.start()
        clock = SimClock(scale=self.scale)
        self.robot = VirtualAGV(self.config, port=self.broker.port, clock=clock)
        self.spy = MQTTClient("spy", "127.0.0.1", self.broker.port)
        await self.spy.connect()
        await self.spy.subscribe(f"{self.robot.topics.prefix}/#")
        self._spy_task = asyncio.create_task(self._spy_loop())
        await self.robot.start()
        self.master = MasterControl(
            "127.0.0.1",
            self.broker.port,
            manufacturer=self.robot.topics.manufacturer,
            serial_number=self.robot.topics.serial_number,
            version=self.version,
        )
        await self.master.connect()
        await self.master.next_state(timeout=5)  # robot is up and reporting
        return self

    async def __aexit__(self, *exc) -> None:
        if self.master is not None:
            await self.master.disconnect()
        if self._spy_task is not None:
            self._spy_task.cancel()
        if self.spy is not None and self.spy.connected:
            await self.spy.disconnect()
        if self.robot is not None:
            await self.robot.stop()
        if self.broker is not None:
            await self.broker.stop()

    async def _spy_loop(self) -> None:
        assert self.spy is not None
        while True:
            message = await self.spy.messages.get()
            name = message.topic.rsplit("/", 1)[1]
            self.raw_published[name].append(message.payload)
            with contextlib.suppress(UnicodeDecodeError, json.JSONDecodeError):
                self.published[name].append(json.loads(message.payload.decode()))

    # Convenience passthroughs used by most tests.

    @property
    def port(self) -> int:
        assert self.broker is not None
        return self.broker.port

    @property
    def m(self) -> MasterControl:
        assert self.master is not None
        return self.master

    @property
    def r(self) -> VirtualAGV:
        assert self.robot is not None
        return self.robot


def straight_order(version: str = "3.0.0", *, n: int = 3, horizon: int = 0, x0: float = 0.0):
    """n released nodes in a line (1 m apart) + optional unreleased horizon."""
    from vda5050_emulator import make_edge, make_node

    total = n + horizon
    nodes = [
        make_node(f"n{i}", 2 * i, x=x0 + float(i), y=0.0, released=i < n) for i in range(total)
    ]
    edges = [
        make_edge(
            f"e{i}",
            2 * i + 1,
            released=i < n - 1,
            start_node_id=f"n{i}",
            end_node_id=f"n{i + 1}",
            version=version,
        )
        for i in range(total - 1)
    ]
    return nodes, edges


async def await_error(stack: Stack, error_type: str, timeout: float = 10.0) -> dict:
    state = await stack.m.next_state(
        lambda s: any(e["errorType"] == error_type for e in s["errors"]), timeout=timeout
    )
    return next(e for e in state["errors"] if e["errorType"] == error_type)
