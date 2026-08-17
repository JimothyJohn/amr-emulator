"""Torture for the ARCL emulator: connection floods, half-open clients, queue
races, oversized input and e-stops in every job phase — the abuse a fleet
server sees on a real factory network."""

from __future__ import annotations

import asyncio

import pytest
from arcl_emulator import ArclServer, Sim
from test_arcl_protocol import Client, Stack, run

pytestmark = []


async def _drain_sessions(server: ArclServer, expected: int, timeout: float = 5.0) -> int:
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        if len(server._sessions) <= expected:
            break
        await asyncio.sleep(0.05)
    return len(server._sessions)


@pytest.mark.integration
def test_hundred_simultaneous_clients():
    async def body():
        async with Stack() as stack:
            clients = [Client(stack.server.port) for _ in range(100)]
            await asyncio.gather(*(c.connect() for c in clients))
            responses = await asyncio.gather(*(c.cmd("oneLineStatus", "Status:") for c in clients))
            assert all(any("StateOfCharge" in line for line in r) for r in responses)
            await asyncio.gather(*(c.close() for c in clients))
            remaining = await _drain_sessions(stack.server, expected=1)
            assert remaining <= 1, f"{remaining} sessions leaked after 100-client storm"

    run(body())


def test_wrong_password_flood_leaves_server_clean():
    async def body():
        async with Stack() as stack:

            async def bad_attempt():
                reader, writer = await asyncio.open_connection("127.0.0.1", stack.server.port)
                await reader.readline()  # Enter password:
                writer.write(b"letmein\r\n")
                await writer.drain()
                line = await reader.readline()
                assert b"Incorrect password" in line
                writer.close()

            await asyncio.gather(*(bad_attempt() for _ in range(50)))
            remaining = await _drain_sessions(stack.server, expected=1)
            assert remaining <= 1
            # A legitimate login still works and queue state is untouched.
            fresh = Client(stack.server.port)
            await fresh.connect()
            lines = await fresh.cmd("queueShow", "EndQueueShow")
            assert lines[-1] == "EndQueueShow"
            await fresh.close()

    run(body())


def test_half_open_connections_are_reaped_by_login_timeout():
    async def body():
        server = ArclServer(port=0, sim=Sim(time_scale=100.0), login_timeout=0.3)
        await server.start()
        try:
            writers = []
            for _ in range(20):
                _reader, writer = await asyncio.open_connection("127.0.0.1", server.port)
                writers.append(writer)  # never send the password
            await asyncio.sleep(0.1)
            assert len(server._sessions) >= 1  # slots held while pending
            remaining = await _drain_sessions(server, expected=0, timeout=5.0)
            assert remaining == 0, f"{remaining} half-open sessions leaked past login timeout"
            for writer in writers:
                writer.close()
            # Server still serves logins afterwards.
            client = Client(server.port)
            await client.connect()
            await client.cmd("oneLineStatus", "Status:")
            await client.close()
        finally:
            await server.stop()

    run(body())


def test_binary_garbage_after_login_is_survivable():
    async def body():
        async with Stack() as stack:
            rogue = Client(stack.server.port)
            await rogue.connect()
            assert rogue.writer is not None
            rogue.writer.write(b"\x00\xff\xfe\x01" * 200 + b"\r\n")
            rogue.writer.write("émoji 🤖 ligne\r\n".encode())
            rogue.writer.write(b"\r\n\r\n\r\n")
            await rogue.writer.drain()
            # The session survives garbage and still answers commands.
            lines = await rogue.cmd("oneLineStatus", "Status:")
            assert any("StateOfCharge" in line for line in lines)
            # And other sessions were never disturbed.
            lines = await stack.client.cmd("oneLineStatus", "Status:")
            assert any("StateOfCharge" in line for line in lines)
            await rogue.close()

    run(body())


@pytest.mark.integration
def test_fifty_queue_pickups_from_five_clients_race_cleanly():
    async def body():
        async with Stack(time_scale=400.0) as stack:
            clients = [Client(stack.server.port) for _ in range(5)]
            await asyncio.gather(*(c.connect() for c in clients))
            for c in clients:
                await c.cmd("echo off", "Echo: off")

            async def enqueue(client: Client, count: int) -> list[str]:
                ids = []
                for _ in range(count):
                    lines = await client.cmd("qp Goal1", "successfully queued")
                    confirm = lines[-1]
                    ids.append(confirm.split(" id ")[1].split(" ")[0].rstrip(","))
                return ids

            all_ids = await asyncio.gather(*(enqueue(c, 10) for c in clients))
            flat = [item for ids in all_ids for item in ids]
            assert len(flat) == 50 and len(set(flat)) == 50, "duplicate queue item ids"

            # Wait until the whole queue drains on the observer client.
            completed: set[str] = set()
            while len(completed) < 50:
                line = await asyncio.wait_for(stack.client.broadcasts.get(), timeout=30)
                parts = line.split()
                if line.startswith("QueueUpdate:") and "Completed" in parts:
                    completed.add(parts[1])
            assert completed == set(flat)

            # Exactly-once terminal transition per item on a second observer.
            terminal_counts: dict[str, int] = {}
            observer = clients[0]
            while not observer.broadcasts.empty():
                line = observer.broadcasts.get_nowait()
                parts = line.split()
                if line.startswith("QueueUpdate:") and "Completed" in parts:
                    terminal_counts[parts[1]] = terminal_counts.get(parts[1], 0) + 1
            assert all(count == 1 for count in terminal_counts.values()), terminal_counts
            await asyncio.gather(*(c.close() for c in clients))

    run(body())


def test_cancel_racing_completion_yields_single_terminal_state():
    async def body():
        async with Stack(time_scale=300.0) as stack:
            for round_number in range(6):
                lines = await stack.client.cmd(
                    f"qp Goal{1 + round_number % 3}", "successfully queued"
                )
                item_id = lines[-1].split(" id ")[1].split(" ")[0].rstrip(",")
                # Spam cancels while the job runs/completes.
                for _ in range(5):
                    await stack.client.cmd(f"qc id {item_id}", "cancelled")
                    await asyncio.sleep(0.01)
                # Collect this item's terminal broadcasts.
                terminals = []
                deadline = asyncio.get_event_loop().time() + 10
                while asyncio.get_event_loop().time() < deadline:
                    try:
                        line = await asyncio.wait_for(stack.client.broadcasts.get(), timeout=0.4)
                    except TimeoutError:
                        if terminals:
                            break
                        continue
                    parts = line.split()
                    if parts[1] == item_id and ("Completed" in parts or "Cancelled" in parts):
                        terminals.append("Completed" if "Completed" in parts else "Cancelled")
                assert len(terminals) == 1, (
                    f"job {item_id} produced terminal broadcasts {terminals}"
                )

    run(body())


def test_goal_names_with_spaces_via_quoting():
    async def body():
        async with Stack() as stack:
            # Input quoting is shlex-style (the manual shows goals quoted in
            # RESPONSES; input quoting is undocumented in I617-E-02's command
            # table, so this is emulator-documented behavior).
            stack.server.sim.goals["Aisle 7 Pickup"] = (1000, 0, 0)
            lines = await stack.client.cmd('queuePickup "Aisle 7 Pickup"', "successfully queued")
            assert 'goal "Aisle 7 Pickup"' in lines[-1]
            lines = await stack.client.cmd("queueShow", "EndQueueShow")
            assert any('Goal "Aisle 7 Pickup"' in line for line in lines)

    run(body())


def test_oversized_input_lines_are_safe():
    async def body():
        async with Stack() as stack:
            # ~2000-char goal name fits in a line: proper two-line error.
            long_goal = "G" * 2000
            lines = await stack.client.cmd(f"queuePickup {long_goal}", "CommandErrorDescription")
            assert any("No goal" in line for line in lines)
            # >4096-char line: dropped silently (documented), session lives.
            assert stack.client.writer is not None
            stack.client.writer.write(b"queuePickup " + b"H" * 6000 + b"\r\n")
            await stack.client.writer.drain()
            lines = await stack.client.cmd("oneLineStatus", "Status:")
            assert any("StateOfCharge" in line for line in lines)
            # >64KB line overruns the stream reader: that session closes, the
            # server and other sessions are unharmed (documented).
            rogue = Client(stack.server.port)
            await rogue.connect()
            assert rogue.writer is not None
            rogue.writer.write(b"say " + b"Z" * 70000 + b"\r\n")
            await rogue.writer.drain()
            await rogue.close()
            lines = await stack.client.cmd("oneLineStatus", "Status:")
            assert any("StateOfCharge" in line for line in lines)

    run(body())


def test_estop_in_every_job_phase_deterministic():
    """Direct Sim stepping: e-stop freezes the lifecycle in whatever phase it
    hits — Pending stays Pending, Driving freezes mid-path — and the job
    completes normally after the e-stop clears."""
    for stop_after_steps in (0, 1, 3, 8):
        sim = Sim(start_epoch=1_700_000_000.0)
        broadcasts: list[str] = []
        sim.broadcast = lambda line, sink=broadcasts: sink.append(line)
        job = sim.queue_pickup("Goal1", 10, None)
        for _ in range(stop_after_steps):
            sim._advance(1.0)
        phase = (job.status, job.substatus)
        sim.estop = True
        frozen_position = (sim.x, sim.y)
        for _ in range(20):
            sim._advance(1.0)
        assert (job.status, job.substatus) == phase, "lifecycle advanced under e-stop"
        assert (sim.x, sim.y) == frozen_position, "robot moved under e-stop"
        sim.estop = False
        for _ in range(60):
            sim._advance(1.0)
            if job.status == "Completed":
                break
        assert job.status == "Completed", f"job stuck after e-stop clear from phase {phase}"
        terminal = [line for line in broadcasts if " Completed " in line]
        assert len(terminal) == 1


def test_dock_undock_churn_during_queued_job():
    async def body():
        async with Stack(time_scale=300.0) as stack:
            await stack.client.cmd("qp Goal2", "successfully queued")
            seen: list[str] = []

            async def churn_once() -> None:
                # dock always broadcasts a Docked line…
                seen.extend(await stack.client.bcmd("dock", "Docked"))
                # …but job allocation silently undocks the robot, so undock
                # may legitimately answer "Robot is not docked" on the
                # RESPONSE stream instead of broadcasting Undocked. Accept
                # either outcome; the point is that churn cannot wedge or
                # crash the server.
                assert stack.client.writer is not None
                stack.client.writer.write(b"undock\r\n")
                await stack.client.writer.drain()
                response_wait = asyncio.ensure_future(stack.client.responses.get())
                broadcast_wait = asyncio.ensure_future(stack.client.until_broadcast("Undocked"))
                done, pending = await asyncio.wait(
                    {response_wait, broadcast_wait},
                    timeout=10,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                assert done, "undock produced no reaction at all"
                for task in done:
                    result = task.result()
                    if isinstance(result, list):
                        seen.extend(result)
                    else:
                        assert "undock" in result or "CommandError" in result, result

            for _ in range(6):
                await churn_once()
            deadline = asyncio.get_event_loop().time() + 15
            while not any("Completed" in line for line in seen):
                assert asyncio.get_event_loop().time() < deadline, seen[-5:]
                seen.append(await asyncio.wait_for(stack.client.broadcasts.get(), timeout=15))
            lines = await stack.client.cmd("oneLineStatus", "Status:")
            assert any("StateOfCharge" in line for line in lines)

    run(body())
