"""Sender ↔ receiver integration over real sockets, on simulated time.

The robot is the real MassRoboticsAMR over the real WebSocket stack against
the real InteropReceiver — no mocks — with SimClock scaling so multi-minute
patrols take milliseconds of wall time.
"""

import asyncio
import json

from massrobotics_emulator import InteropReceiver, MassRoboticsAMR, vecna_config
from massrobotics_emulator import ws as ws_module
from vda5050_emulator.clock import SimClock

TIMEOUT = 30.0


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, TIMEOUT))


class Stack:
    def __init__(self, *, robots: int = 1, model: str = "APT", scale: float = 200.0, **config):
        self.clock = SimClock(scale=scale)
        self.receiver = InteropReceiver()
        self.robots = [
            MassRoboticsAMR(
                vecna_config(model, serial_number=f"{model}-{n + 1:04d}", **config),
                clock=self.clock,
            )
            for n in range(robots)
        ]

    async def __aenter__(self):
        await self.receiver.start()
        for robot in self.robots:
            await robot.start(self.receiver.uri)
        return self

    async def __aexit__(self, *exc):
        for robot in self.robots:
            await robot.stop()
        await self.receiver.stop()


def test_identity_then_status_flow():
    async def scenario():
        async with Stack() as stack:
            (record,) = await stack.receiver.wait_for_robots(1)
            assert record.identity["manufacturerName"] == "Vecna Robotics"
            assert record.identity["robotModel"] == "APT"
            status = await stack.receiver.next_status(record.uuid)
            assert status["operationalState"] == "idle"
            assert record.problems == []

    run(scenario())


def test_navigation_visible_end_to_end():
    async def scenario():
        async with Stack() as stack:
            (record,) = await stack.receiver.wait_for_robots(1)
            robot = stack.robots[0]
            robot.navigate_to(30.0, 0.0)
            navigating = await stack.receiver.next_status(
                record.uuid, lambda s: s["operationalState"] == "navigating"
            )
            assert navigating["destinations"][0]["x"] == 30.0
            await robot.wait_for_arrival()
            arrived = await stack.receiver.next_status(
                record.uuid,
                lambda s: s["operationalState"] == "idle" and s["location"]["x"] == 30.0,
            )
            assert arrived["velocity"]["linear"] == 0.0
            assert record.problems == []

    run(scenario())


def test_fleet_of_four_vecna_models_all_validate():
    async def scenario():
        clock = SimClock(scale=200.0)
        receiver = InteropReceiver()
        await receiver.start()
        robots = [
            MassRoboticsAMR(vecna_config(model), clock=clock)
            for model in ("APT", "ATG", "AFL", "CPJ")
        ]
        for robot in robots:
            await robot.start(receiver.uri)
        try:
            records = await receiver.wait_for_robots(4)
            models = {record.identity["robotModel"] for record in records if record.identity}
            assert models == {"APT", "ATG", "AFL", "CPJ"}
            for record in records:
                await receiver.next_status(record.uuid)
                assert record.problems == []
        finally:
            for robot in robots:
                await robot.stop()
            await receiver.stop()

    run(scenario())


def test_battery_drains_and_charges_on_sim_time():
    async def scenario():
        async with Stack(scale=400.0, battery_percentage=50.0) as stack:
            (record,) = await stack.receiver.wait_for_robots(1)
            first = await stack.receiver.next_status(record.uuid)
            drained = await stack.receiver.next_status(
                record.uuid, lambda s: s["batteryPercentage"] < first["batteryPercentage"]
            )
            stack.robots[0].set_charging(True)
            charging = await stack.receiver.next_status(
                record.uuid, lambda s: s["operationalState"] == "charging"
            )
            recovered = await stack.receiver.next_status(
                record.uuid,
                lambda s: s["batteryPercentage"] > charging["batteryPercentage"],
            )
            assert recovered["batteryPercentage"] > drained["batteryPercentage"]

    run(scenario())


def test_receiver_records_invalid_messages_without_dropping_the_robot():
    async def scenario():
        async with Stack() as stack:
            (record,) = await stack.receiver.wait_for_robots(1)
            # A raw rogue client claiming the same uuid sends garbage the
            # schema rejects: recorded as problems, attributable, not fatal.
            rogue = await ws_module.connect(stack.receiver.uri)
            await rogue.send_text(json.dumps({"uuid": record.uuid, "operationalState": "flying"}))
            await rogue.send_text("this is not json")  # attributed: uuid known
            stray = await ws_module.connect(stack.receiver.uri)
            await stray.send_text("garbage before any uuid")  # unattributable

            def has_problems():
                return len(record.problems) >= 2 and len(stack.receiver.rejected) >= 1

            for _ in range(100):
                if has_problems():
                    break
                await asyncio.sleep(0.05)
            assert has_problems()
            kind, problems = record.problems[0]
            assert kind == "statusReport"
            assert any("flying" in problem or "location" in problem for problem in problems)
            # the legitimate robot keeps streaming validly
            await stack.receiver.next_status(record.uuid)
            await rogue.close()
            await stray.close()

    run(scenario())


def test_disconnect_marks_robot_offline_at_receiver():
    async def scenario():
        async with Stack() as stack:
            (record,) = await stack.receiver.wait_for_robots(1)
            await stack.robots[0].stop()
            for _ in range(100):
                if not record.connected:
                    break
                await asyncio.sleep(0.05)
            assert not record.connected

    run(scenario())


def test_concurrent_fleet_no_cross_talk():
    async def scenario():
        async with Stack(robots=6, scale=500.0) as stack:
            records = await stack.receiver.wait_for_robots(6)
            for n, robot in enumerate(stack.robots):
                robot.navigate_to(10.0 + n, 42.0)
            await asyncio.gather(*(robot.wait_for_arrival() for robot in stack.robots))
            by_serial = sorted(records, key=lambda r: r.identity["robotSerialNumber"])
            for n, record in enumerate(by_serial):
                arrived = await stack.receiver.next_status(
                    record.uuid,
                    lambda s, n=n: (s["location"]["x"], s["location"]["y"]) == (10.0 + n, 42.0),
                )
                assert arrived["uuid"] == record.uuid
                assert record.problems == []

    run(scenario())
