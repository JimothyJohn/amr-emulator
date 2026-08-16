"""Protocol conformance against the response formats transcribed from
I617-E-02 (see specs/arcl_commands.json for per-command manual pages)."""

from __future__ import annotations

import asyncio
import json
import re
from importlib import resources

from arcl_emulator import ArclServer, Sim

TIMEOUT = 20.0


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, TIMEOUT))


class Client:
    """Test client that separates command responses from asynchronous
    broadcast lines (QueueUpdate:/Fault:/DockingState:/ArclText:)."""

    BROADCASTS = ("QueueUpdate:", "Fault:", "ArclText:", "DockingState:")

    def __init__(self, port: int) -> None:
        self.port = port
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.responses: asyncio.Queue[str] = asyncio.Queue()
        self.broadcasts: asyncio.Queue[str] = asyncio.Queue()
        self._pump: asyncio.Task | None = None

    async def connect(self, password: str = "adept") -> list[str]:  # noqa: S107 — test default
        self.reader, self.writer = await asyncio.open_connection("127.0.0.1", self.port)
        prompt = await self._raw_line()
        assert prompt == "Enter password:"
        self.writer.write((password + "\r\n").encode())
        banner = []
        while True:
            line = await self._raw_line()
            banner.append(line)
            if line == "End of commands":
                break
        self._pump = asyncio.create_task(self._pump_lines())
        return banner

    async def _raw_line(self) -> str:
        assert self.reader is not None
        raw = await self.reader.readline()
        if not raw:
            raise ConnectionError("closed")
        return raw.decode().rstrip("\r\n")

    async def _pump_lines(self) -> None:
        while True:
            try:
                line = await self._raw_line()
            except (ConnectionError, asyncio.IncompleteReadError):
                return
            if line.startswith(self.BROADCASTS):
                await self.broadcasts.put(line)
            else:
                await self.responses.put(line)

    async def until(self, sentinel: str, prefix: bool = False) -> list[str]:
        del prefix  # containment matching covers every sentinel style used here
        lines = []
        while True:
            line = await self.responses.get()
            lines.append(line)
            if sentinel in line:
                return lines

    async def until_broadcast(self, sentinel: str, prefix: bool = True) -> list[str]:
        del prefix
        lines = []
        while True:
            line = await self.broadcasts.get()
            lines.append(line)
            if sentinel in line:
                return lines

    async def cmd(self, text: str, sentinel: str, prefix: bool = False) -> list[str]:
        assert self.writer is not None
        self.writer.write((text + "\r\n").encode())
        await self.writer.drain()
        return await self.until(sentinel, prefix=prefix)

    async def bcmd(self, text: str, sentinel: str) -> list[str]:
        """Send a command whose interesting output arrives as broadcasts."""
        assert self.writer is not None
        self.writer.write((text + "\r\n").encode())
        await self.writer.drain()
        return await self.until_broadcast(sentinel, prefix=True)

    async def close(self) -> None:
        if self._pump is not None:
            self._pump.cancel()
        if self.writer is not None:
            self.writer.close()


class Stack:
    def __init__(self, *, time_scale: float = 200.0) -> None:
        self.server = ArclServer(port=0, sim=Sim(time_scale=time_scale))

    async def __aenter__(self):
        await self.server.start()
        self.client = Client(self.server.port)
        await self.client.connect()
        await self.client.cmd("echo off", "Echo: off")
        return self

    async def __aexit__(self, *exc):
        await self.client.close()
        await self.server.stop()


def test_login_banner_lists_commands():
    async def body():
        async with Stack() as stack:
            fresh = Client(stack.server.port)
            banner = await fresh.connect()
            assert "Commands:" in banner
            assert any(line.startswith("queuePickup") for line in banner)
            assert banner[-1] == "End of commands"
            await fresh.close()

    run(body())


def test_wrong_password_closes_connection():
    async def body():
        async with Stack() as stack:
            reader, writer = await asyncio.open_connection("127.0.0.1", stack.server.port)
            await reader.readline()
            writer.write(b"nope\r\n")
            line = (await reader.readline()).decode()
            assert "Incorrect password" in line
            assert await reader.read(64) == b""  # server closed it
            writer.close()

    run(body())


def test_status_five_documented_lines():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd("status", "Temperature:", prefix=True)
            assert lines[0].startswith("Status: ")
            assert lines[1].startswith("StateOfCharge: ")
            assert re.match(r"Location: -?\d+ -?\d+ -?\d+$", lines[2])
            assert lines[3].startswith("LocalizationScore: ")
            assert lines[4].startswith("Temperature: ")

    run(body())


def test_one_line_status_format():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd("onelinestatus", "Status:", prefix=True)
            assert re.match(
                r"Status: .+ StateOfCharge: [\d.]+ Location: -?\d+ -?\d+ -?\d+ "
                r"Temperature: -?\d+$",
                lines[-1],
            )

    run(body())


def test_get_goals_and_routes():
    async def body():
        async with Stack() as stack:
            goals = await stack.client.cmd("getgoals", "End of goals")
            assert "Goal: Goal1" in goals and "Goal: Standby" in goals
            routes = await stack.client.cmd("getroutes", "End of routes")
            assert routes[0] == "Routes"
            assert any(line.startswith("Route: ") for line in routes)

    run(body())


def test_get_date_time_format():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd("getdatetime", "DateTime:", prefix=True)
            assert re.match(r"DateTime: \d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$", lines[-1])

    run(body())


def test_odometer_and_reset():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd("odometer", "Odometer:", prefix=True)
            assert re.match(r"Odometer: \d+ mm \d+ deg \d+ sec$", lines[-1])
            lines = await stack.client.cmd("odometerreset", "Reset odometer")
            assert lines[-1] == "Reset odometer"

    run(body())


def test_unknown_command_two_line_error():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd(
                "summonRobotArmy now", "CommandErrorDescription:", prefix=True
            )
            assert lines[-2] == "CommandError: summonRobotArmy now"
            assert lines[-1].startswith("CommandErrorDescription: Unknown command")

    run(body())


def test_queue_pickup_bad_goal_matches_manual_example():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd(
                "queuepickup goal2", "CommandErrorDescription:", prefix=True
            )
            assert "CommandError: queuePickup goal2" in lines
            assert "CommandErrorDescription: No goal 'goal2'" in lines

    run(body())


def test_shortcuts_resolve():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd("qs", "EndQueueShow")
            assert lines[-1] == "EndQueueShow"
            lines = await stack.client.cmd("afq", "End of ApplicationFaultQuery")
            assert lines[-1] == "End of ApplicationFaultQuery"

    run(body())


def test_application_faults_lifecycle():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.cmd(
                'applicationfaultset faulTest "Fault test"', "ApplicationFaultSet", prefix=True
            )
            assert lines[-1] == "ApplicationFaultSet set faulTest"
            fault = await stack.client.until_broadcast("Fault: ")
            assert fault[-1].startswith("Fault: Fault_Driving_Critical_Application faulTest")
            lines = await stack.client.cmd("applicationfaultquery", "End of ApplicationFaultQuery")
            assert any("faulTest" in line for line in lines)
            lines = await stack.client.cmd(
                "applicationfaultclear faulTest", "ApplicationFaultClear", prefix=True
            )
            assert lines[-1] == "ApplicationFaultClear cleared faulTest"

    run(body())


def test_dock_undock_states():
    async def body():
        async with Stack() as stack:
            lines = await stack.client.bcmd("dock", "DockingState: Docked")
            assert lines[-1].startswith("DockingState: Docked")
            status = await stack.client.cmd("status", "Temperature:", prefix=True)
            assert "DockingState: Docked" in status[0]
            lines = await stack.client.bcmd("undock", "DockingState: Undocked")
            assert lines[-1].startswith("DockingState: Undocked")

    run(body())


def test_garbage_never_kills_the_server():
    async def body():
        async with Stack() as stack:
            reader, writer = await asyncio.open_connection("127.0.0.1", stack.server.port)
            await reader.readline()
            writer.write(b"adept\r\n")
            writer.write(b"\x00\xff\xfe" * 200 + b"\r\n")
            writer.write(b"a" * 10_000 + b"\r\n")
            writer.write(b'say "unterminated\r\n')
            writer.write(b"\r\n\r\n")
            await writer.drain()
            writer.close()
            # the server still serves a healthy client afterwards
            lines = await stack.client.cmd("getgoals", "End of goals")
            assert lines[-1] == "End of goals"

    run(body())


def test_echo_on_repeats_input():
    async def body():
        async with Stack() as stack:
            fresh = Client(stack.server.port)
            await fresh.connect()  # echo defaults on
            lines = await fresh.cmd("getgoals", "End of goals")
            assert lines[0] == "getgoals"  # echoed back
            await fresh.close()

    run(body())


def test_command_table_pages_recorded():
    table = json.loads(
        (resources.files("arcl_emulator") / "specs" / "arcl_commands.json").read_text()
    )
    registry = json.loads(
        (resources.files("arcl_emulator") / "specs" / "registry.json").read_text()
    )
    assert registry["source"]["sha256"].startswith("5d06a0a9")
    for name, entry in table["commands"].items():
        if name.startswith("_") or name in ("errors", "job_status_conditions"):
            continue
        assert "page" in entry, f"{name} lacks a manual page citation"
