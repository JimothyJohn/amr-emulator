"""Fleet queuing lifecycle, simulation determinism, concurrency and the
non-standard fault-injection channel."""

from __future__ import annotations

import asyncio
import re

from arcl_emulator import ArclServer, Sim
from test_arcl_protocol import Client, Stack, run


def test_queue_pickup_full_lifecycle_to_completed():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd(
                "queuepickup Goal1 11 xyz", "successfully queued", prefix=True
            )
            confirm = lines[-1]
            assert re.match(
                r'queuepickup goal "Goal1" with priority 11, id PICKUP\d+ '
                r"and job_id xyz successfully queued$",
                confirm,
            )
            updates = await stack.client.until_broadcast("QueueUpdate: PICKUP1 xyz 11 Completed")
            texts = "\n".join(updates)
            assert "Pending None" in texts
            assert "InProgress Allocated" in texts
            assert "InProgress Driving" in texts
            assert "InProgress AfterPickup" in texts
            # robot physically arrived at Goal1 (5000, 0)
            status = await stack.client.cmd("status", "Temperature:", prefix=True)
            assert "Arrived at Goal1" in status[0]
            assert status[2] == "Location: 5000 0 0"

    run(body())


def test_queue_update_line_matches_documented_shape():
    async def body():
        async with Stack() as stack:
            await stack.client.cmd("queuepickup Goal2", "successfully queued", prefix=True)
            update = (await stack.client.until_broadcast("QueueUpdate:"))[-1]
            assert re.match(
                r"QueueUpdate: PICKUP\d+ JOB\d+ 10 Pending None "
                r'Goal "Goal2" none \d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} None None 0$',
                update,
            )

    run(body())


def test_pickup_dropoff_ordering():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd(
                "queuepickupdropoff Goal1 Goal3 default job7",
                "successfully queued",
                prefix=True,
            )
            assert "ids PICKUP1 and DROPOFF1" in lines[-1]
            await stack.client.until_broadcast("QueueUpdate: PICKUP1 job7 10 Completed")
            await stack.client.until_broadcast("QueueUpdate: DROPOFF1 job7 10 Completed")
            status = await stack.client.cmd("status", "Temperature:", prefix=True)
            assert "Arrived at Goal3" in status[0]

    run(body())


def test_queue_query_by_job_id():
    async def body():
        async with Stack() as stack:
            await stack.client.cmd("queuepickup Goal1 10 qjob", "successfully queued", True)
            lines = await stack.client.cmd("queuequery jobid qjob probe", "EndQueueQuery")
            rows = [line for line in lines if line.startswith("QueueQuery:")]
            assert rows, lines
            assert " probe " in rows[0] and "qjob" in rows[0]
            lines = await stack.client.cmd("queuequery jobid missing", "EndQueueQuery")
            assert not any(line.startswith("QueueQuery:") for line in lines)

    run(body())


def test_queue_cancel_by_id():
    async def body():
        async with Stack(time_scale=1.0) as stack:  # slow: job stays pending/driving
            await stack.client.cmd("queuepickup Goal2 10 cjob", "successfully queued", True)
            lines = await stack.client.cmd("queuecancel id PICKUP1", "cancelled", prefix=True)
            assert "cancelled 1 item(s)" in lines[-1]
            rows = await stack.client.cmd("queuequery jobid cjob", "EndQueueQuery")
            assert any("Cancelled" in line for line in rows)

    run(body())


def test_estop_blocks_and_release_completes():
    async def body():
        async with Stack() as stack:
            await stack.client.cmd("emulator estop on", "Emulator: estop on")
            await stack.client.cmd("queuepickup Goal1 10 ejob", "successfully queued", True)
            await asyncio.sleep(0.3)  # plenty of simulated time at scale 200
            rows = await stack.client.cmd("queuequery jobid ejob", "EndQueueQuery")
            assert not any("Completed" in line for line in rows), rows
            await stack.client.cmd("emulator estop off", "Emulator: estop off")
            await stack.client.until_broadcast("QueueUpdate: PICKUP1 ejob 10 Completed")

    run(body())


def test_emulator_battery_and_teleport():
    async def body():
        async with Stack() as stack:
            await stack.client.cmd("emulator battery 7.5", "Emulator: battery 7.5")
            lines = await stack.client.cmd("status", "Temperature:", prefix=True)
            assert lines[1].startswith("StateOfCharge: 7.")
            await stack.client.cmd("emulator teleport 1000 2000 90", "Emulator: teleport", True)
            lines = await stack.client.cmd("status", "Temperature:", prefix=True)
            assert lines[2] == "Location: 1000 2000 90"

    run(body())


def test_broadcasts_reach_all_clients():
    async def body():
        async with Stack() as stack:
            second = Client(stack.server.port)
            await second.connect()
            await second.cmd("echo off", "Echo: off")
            await stack.client.bcmd("arclsendtext hello fleet", "ArclText: hello fleet")
            got = await second.until_broadcast("ArclText: hello fleet")
            assert got[-1] == "ArclText: hello fleet"
            await second.close()

    run(body())


def test_concurrent_clients_during_job():
    async def body():
        async with Stack() as stack:
            clients = []
            for _ in range(10):
                c = Client(stack.server.port)
                await c.connect()
                await c.cmd("echo off", "Echo: off")
                clients.append(c)
            await stack.client.cmd("queuepickup Goal2 10 cc", "successfully queued", True)

            async def query(c: Client) -> bool:
                lines = await c.cmd("queuequery jobid cc", "EndQueueQuery")
                return lines[-1] == "EndQueueQuery"

            results = await asyncio.gather(*(query(c) for c in clients))
            assert all(results)
            await stack.client.until_broadcast("QueueUpdate: PICKUP1 cc 10 Completed")
            for c in clients:
                await c.close()

    run(body())


def test_sim_advance_is_deterministic():
    def trajectory() -> list[tuple[float, float]]:
        sim = Sim(start_epoch=1_700_000_000.0)
        sim.broadcast = lambda line: None
        sim.queue_pickup("Goal2", 10, "d1")
        points = []
        for _ in range(200):
            sim._advance(0.5)
            points.append((round(sim.x, 3), round(sim.y, 3)))
        return points

    first, second = trajectory(), trajectory()
    assert first == second
    assert first[-1] == (5000.0, 5000.0)


def test_stop_interrupts_active_job():
    async def body():
        async with Stack(time_scale=1.0) as stack:
            await stack.client.cmd("queuepickup Goal2 10 sjob", "successfully queued", True)
            await stack.client.until_broadcast("QueueUpdate: PICKUP1 sjob 10 InProgress Driving")
            lines = await stack.client.cmd("stop", "Stopping")
            assert lines[-1] == "Stopping"
            rows = await stack.client.cmd("queuequery jobid sjob", "EndQueueQuery")
            assert any("Interrupted" in line for line in rows)

    run(body())


def test_docked_robot_charges():
    async def body():
        async with Stack() as stack:
            await stack.client.cmd("emulator battery 50", "Emulator: battery 50.0")
            await stack.client.bcmd("dock", "DockingState: Docked")
            await asyncio.sleep(0.5)  # ~100 simulated seconds at scale 200
            lines = await stack.client.cmd("status", "Temperature:", prefix=True)
            charge = float(lines[1].split(": ")[1])
            assert charge > 50.0

    run(body())


def test_server_port_zero_binds_ephemeral():
    async def body():
        server = ArclServer(port=0)
        await server.start()
        assert server.port != 0
        await server.stop()

    run(body())
