"""Shared harness: one broker + N emulated robots + one FleetMaster.

Same conventions as the emulator's vda_harness: async bodies run through
``asyncio.run`` inside sync tests (no pytest-asyncio), with a hard timeout
so a deadlock fails instead of hanging, all on fast simulated time. The
robots are the real VirtualAGV over the real embedded broker — the master
is exercised against the same counterpart implementation every conformance
test in this repo trusts, not against mocks.
"""

from __future__ import annotations

import asyncio

from vda5050_emulator import AGVConfig, Broker, VirtualAGV
from vda5050_emulator.clock import SimClock
from vda5050_master import FleetMaster, Mission, MissionController, Waypoint

TIMEOUT = 30.0


def run(coro, timeout: float = TIMEOUT):
    return asyncio.run(asyncio.wait_for(coro, timeout))


class FleetStack:
    """Broker + ``robots`` VirtualAGVs (r0, r1, …) + connected FleetMaster."""

    def __init__(
        self, version: str = "3.0.0", *, robots: int = 1, scale: float = 200.0, **config
    ) -> None:
        config.setdefault("visualization_interval", 0)
        self.version = version
        self.scale = scale
        self.config = config
        self.count = robots
        self.broker: Broker | None = None
        self.robots: list[VirtualAGV] = []
        self.master: FleetMaster | None = None
        self.controller: MissionController | None = None

    async def __aenter__(self) -> FleetStack:
        self.broker = Broker(port=0)
        await self.broker.start()
        clock = SimClock(scale=self.scale)
        for i in range(self.count):
            robot = VirtualAGV(
                AGVConfig(version=self.version, serial_number=f"r{i}", **self.config),
                port=self.broker.port,
                clock=clock,
            )
            self.robots.append(robot)
            await robot.start()
        self.master = FleetMaster("127.0.0.1", self.broker.port, version=self.version, clock=clock)
        await self.master.connect()
        await self.master.wait_for_robots(self.count, timeout=5)
        self.controller = MissionController(self.master)
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self.controller is not None:
            await self.controller.shutdown()
        if self.master is not None:
            await self.master.disconnect()
        for robot in self.robots:
            await robot.stop()
        if self.broker is not None:
            await self.broker.stop()

    @property
    def m(self) -> FleetMaster:
        assert self.master is not None
        return self.master

    @property
    def c(self) -> MissionController:
        assert self.controller is not None
        return self.controller


def line_mission(
    n: int = 3,
    *,
    x0: float = 0.0,
    name: str = "line",
    actions_at: dict[int, list[dict]] | None = None,
) -> Mission:
    """n waypoints in a line, 1 m apart, starting where the robots spawn."""
    return Mission(
        [
            Waypoint(x=x0 + float(i), y=0.0, actions=tuple((actions_at or {}).get(i, ())))
            for i in range(n)
        ],
        name=name,
    )
