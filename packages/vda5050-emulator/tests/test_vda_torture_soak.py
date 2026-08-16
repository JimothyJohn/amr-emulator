"""Soak: 60 seconds of continuous mixed traffic against three robots and two
masters on one broker at time-scale 100 — then prove the system is still
healthy: responsive, schema-valid, no stuck errors, no runaway memory."""

from __future__ import annotations

import asyncio
import random
import resource
import sys
import time

import pytest
from vda5050_emulator import (
    AGVConfig,
    Broker,
    MasterControl,
    VirtualAGV,
    make_edge,
    make_node,
)
from vda5050_emulator.clock import SimClock
from vda5050_emulator.validation import validation_errors
from vda_harness import run

pytestmark = pytest.mark.integration

SOAK_SECONDS = 60.0


def _rss_mb() -> float:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / (1024 * 1024) if sys.platform == "darwin" else peak / 1024


def test_sixty_second_mixed_traffic_soak():
    async def body():
        rng = random.Random(1234)  # noqa: S311 — deterministic soak traffic, not crypto
        broker = Broker(port=0)
        await broker.start()
        clock = SimClock(scale=100.0)
        robots = []
        for i in range(3):
            robot = VirtualAGV(
                AGVConfig(
                    serial_number=f"soak-{i}",
                    visualization_interval=0,
                    min_state_interval=0.05,
                ),
                port=broker.port,
                clock=clock,
            )
            await robot.start()
            robots.append(robot)
        masters = []
        for i, robot in enumerate((*robots, robots[0])[:2]):
            master = MasterControl(
                "127.0.0.1",
                broker.port,
                manufacturer=robot.topics.manufacturer,
                serial_number=robot.topics.serial_number,
                client_id=f"soak-master-{i}",
            )
            await master.connect()
            masters.append(master)

        started = time.monotonic()
        baseline: float | None = None
        counter = 0
        while time.monotonic() - started < SOAK_SECONDS:
            if baseline is None and time.monotonic() - started >= 5:
                baseline = _rss_mb()
            robot = rng.choice(robots)
            master = masters[0] if robot is robots[0] else None
            move = rng.random()
            counter += 1
            if move < 0.4:
                nodes = [
                    make_node("a", 0, x=robot.x, y=robot.y, deviation=50.0),
                    make_node("b", 2, x=robot.x + rng.uniform(0.5, 2), y=robot.y),
                ]
                target = master or masters[1]
                if target.topics.serial_number == robot.topics.serial_number:
                    await target.send_order(nodes, [make_edge("e", 1)], order_id=f"soak-{counter}")
            elif move < 0.6 and master is not None:
                await master.send_instant_action(
                    rng.choice(("cancelOrder", "stateRequest", "startPause", "stopPause"))
                )
            elif move < 0.8:
                robot.inject(
                    emergency_stop=rng.choice(("NONE", "NONE", "MANUAL")),
                    battery={"level": rng.uniform(10, 100)},
                    localized=rng.random() > 0.05,
                )
            else:
                robot.inject(emergency_stop="NONE", localized=True)
            if counter % 100 == 0:
                # A well-behaved master clears settled instant actions (the
                # spec keeps them until clearInstantActions) and a bounded
                # test harness must not hoard every state it ever saw —
                # otherwise the RSS assertion measures the test, not the
                # emulator.
                for master in masters:
                    await master.send_instant_action("clearInstantActions")
                    del master.states[:-50]
                    del master.visualizations[:]
            await asyncio.sleep(0.02)

        # Health checks after the storm.
        for robot in robots:
            robot.inject(emergency_stop="NONE", field_violation=False, localized=True)
        for master in masters:
            probe_started = time.monotonic()
            aid = await master.send_instant_action("stateRequest")
            await master.action_status(aid, statuses=("FINISHED",), timeout=5)
            assert time.monotonic() - probe_started < 1.5, "state probe too slow"
        recent = masters[0].states[-20:]
        assert recent, "no states collected"
        for doc in recent:
            assert not validation_errors("state", doc, tag="3.0.0")
            assert not any(e["errorType"] == "LOCALIZATION_ERROR" for e in doc["errors"]), (
                "cleared condition error still reported"
            )
        assert baseline is not None
        growth = _rss_mb() - baseline
        assert growth < 50, f"RSS grew {growth:.1f} MB during soak"

        for master in masters:
            await master.disconnect()
        for robot in robots:
            await robot.stop()
        await broker.stop()

    run(body(), timeout=SOAK_SECONDS + 60)
