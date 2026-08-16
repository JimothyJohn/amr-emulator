"""ARCL TCP protocol layer: login, command dispatch, broadcasts.

Command syntax and response literals per I617-E-02 (pages cited in
``specs/arcl_commands.json``). Errors use the documented two-line form::

    CommandError: <command> <args>
    CommandErrorDescription: <detail>

Malformed input never terminates the server; a broken client only loses its
own connection.
"""

from __future__ import annotations

import asyncio
import contextlib
import shlex

from .server import DEFAULT_PASSWORD, DEFAULT_PORT, HELP_LINES, SHORTCUTS, Job, Sim, _fmt_dt

MAX_LINE = 4096


class ArclServer:
    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = DEFAULT_PORT,
        password: str = DEFAULT_PASSWORD,
        sim: Sim | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.sim = sim or Sim()
        self.sim.broadcast = self.broadcast
        self._server: asyncio.Server | None = None
        self._sim_task: asyncio.Task | None = None
        self._sessions: set[Session] = set()

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._on_connect, self.host, self.port)
        self.port = self._server.sockets[0].getsockname()[1]
        self._sim_task = asyncio.create_task(self.sim.run())

    async def stop(self) -> None:
        if self._sim_task is not None:
            self._sim_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._sim_task
        for session in list(self._sessions):
            session.close()
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

    def broadcast(self, line: str) -> None:
        for session in list(self._sessions):
            if session.logged_in:
                session.send(line)

    async def _on_connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        session = Session(self, reader, writer)
        self._sessions.add(session)
        try:
            await session.run()
        except (ConnectionError, asyncio.IncompleteReadError, asyncio.LimitOverrunError):
            pass
        except Exception:  # noqa: S110 — one broken client must not kill the server
            pass
        finally:
            self._sessions.discard(session)
            session.close()


class Session:
    def __init__(self, server: ArclServer, reader, writer) -> None:
        self.server = server
        self.sim = server.sim
        self.reader = reader
        self.writer = writer
        self.logged_in = False
        self.echo = self.sim.echo_default

    # -- transport helpers

    def send(self, line: str) -> None:
        with contextlib.suppress(ConnectionError, RuntimeError):
            self.writer.write((line + "\r\n").encode())

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self.writer.close()

    async def _read_line(self) -> str | None:
        try:
            raw = await self.reader.readline()
        except (ValueError, ConnectionError):  # oversized or dropped
            return None
        if not raw:
            return None
        if len(raw) > MAX_LINE:
            return ""
        return raw.decode("utf-8", errors="replace").rstrip("\r\n")

    # -- session lifecycle

    async def run(self) -> None:
        self.send("Enter password:")
        await self.writer.drain()
        password = await self._read_line()
        if password is None:
            return
        if password != self.server.password:
            self.send("Incorrect password. Closing connection.")
            await self.writer.drain()
            return
        self.logged_in = True
        self.send("Welcome to the server.")
        self.send("You are connected to an ARCL emulator (amr-emulator).")
        self.send("Commands:")
        for name, desc in HELP_LINES:
            self.send(f"{name:28s}{desc}")
        self.send("End of commands")
        await self.writer.drain()
        while True:
            line = await self._read_line()
            if line is None:
                return
            if self.echo and line:
                self.send(line)
            if not line.strip():
                await self.writer.drain()
                continue
            if not self._dispatch(line.strip()):
                return
            await self.writer.drain()

    # -- command dispatch

    def _dispatch(self, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            parts = line.split()
        if not parts:
            return True
        word = parts[0].lower()
        word = SHORTCUTS.get(word, word)
        args = parts[1:]
        handler = getattr(self, f"_cmd_{word}", None)
        if handler is None:
            self._error(line, f"Unknown command '{parts[0]}'")
            return True
        return handler(args, line) is not False

    def _error(self, line: str, detail: str) -> None:
        self.send(f"CommandError: {line}")
        self.send(f"CommandErrorDescription: {detail}")

    # -- commands (pages per specs/arcl_commands.json)

    def _cmd_help(self, args, line):
        self.send("Commands:")
        for name, desc in HELP_LINES:
            self.send(f"{name:28s}{desc}")
        self.send("End of commands")

    def _cmd_quit(self, args, line):
        self.send("Goodbye.")
        return False

    def _cmd_echo(self, args, line):
        if not args:
            self.send(f"Echo: {'on' if self.echo else 'off'}")
        elif args[0].lower() in ("on", "off"):
            self.echo = args[0].lower() == "on"
            self.send(f"Echo: {args[0].lower()}")
        else:
            self._error(line, "echo takes 'on' or 'off'")

    def _cmd_status(self, args, line):
        sim = self.sim
        if sim.docking_state != "Undocked":
            status = (
                f"DockingState: {sim.docking_state} ForcedState: Unforced "
                f"ChargeState: {sim.charge_state}"
            )
        else:
            status = sim.status_text
        self.send(f"Status: {status}")
        self.send(f"StateOfCharge: {sim.battery:.1f}")
        self.send(f"Location: {sim.x:.0f} {sim.y:.0f} {sim.heading:.0f}")
        self.send(f"LocalizationScore: {sim.localization_score:.6f}")
        self.send(f"Temperature: {sim.temperature}")

    def _cmd_onelinestatus(self, args, line):
        sim = self.sim
        self.send(
            f"Status: {sim.status_text} StateOfCharge: {sim.battery:.1f} "
            f"Location: {sim.x:.0f} {sim.y:.0f} {sim.heading:.0f} "
            f"Temperature: {sim.temperature}"
        )

    def _cmd_getgoals(self, args, line):
        for name in self.sim.goals:
            self.send(f"Goal: {name}")
        self.send("End of goals")

    def _cmd_getroutes(self, args, line):
        self.send("Routes")
        for name in self.sim.routes:
            self.send(f"Route: {name}")
        self.send("End of routes")

    def _cmd_getdatetime(self, args, line):
        date, clock = _fmt_dt(self.sim.now())
        self.send(f"DateTime: {date} {clock}")

    def _cmd_odometer(self, args, line):
        sim = self.sim
        seconds = int(sim.now() - sim.odometer_start)
        self.send(f"Odometer: {sim.odometer_mm:.0f} mm {sim.odometer_deg:.0f} deg {seconds} sec")

    def _cmd_odometerreset(self, args, line):
        sim = self.sim
        sim.odometer_mm = 0.0
        sim.odometer_deg = 0.0
        sim.odometer_start = sim.now()
        self.send("Reset odometer")

    def _cmd_stop(self, args, line):
        self.send("Stopping")
        sim = self.sim
        for job in sim.jobs:
            if job.status == "InProgress":
                job.status = "Interrupted"
                job.substatus = "None"
                self.server.broadcast(job.update_line())
        sim.status_text = "Stopped"

    def _cmd_dock(self, args, line):
        sim = self.sim
        sim.goals.setdefault("Dock1", (-2000, 0, 180))
        sim.docking_state = "Docking"
        sim.status_text = "Going to Dock1"
        self.send("DockingState: Docking ForcedState: Unforced ChargeState: Not")
        sim.x, sim.y, sim.heading = (float(v) for v in sim.goals["Dock1"])
        sim.docking_state = "Docked"
        sim.charge_state = "Bulk"
        sim.status_text = "Docked"
        self.server.broadcast("DockingState: Docked ForcedState: Unforced ChargeState: Bulk")

    def _cmd_undock(self, args, line):
        sim = self.sim
        if sim.docking_state != "Docked":
            self._error(line, "Robot is not docked")
            return
        sim.docking_state = "Undocking"
        self.send("DockingState: Undocking ForcedState: Unforced ChargeState: Not")
        sim.docking_state = "Undocked"
        sim.charge_state = "Not"
        sim.status_text = "Available"
        self.server.broadcast("DockingState: Undocked ForcedState: Unforced ChargeState: Not")

    def _cmd_say(self, args, line):
        if not args:
            self._error(line, "say requires a string")
            return
        self.send(f'saying "{" ".join(args)}"')

    def _cmd_arclsendtext(self, args, line):
        if not args:
            self._error(line, "arclSendText requires a message")
            return
        self.server.broadcast(f"ArclText: {' '.join(args)}")

    def _cmd_faultsget(self, args, line):
        for name, (fault_id, _short) in self.sim.app_faults.items():
            self.send(f"FaultList: {fault_id} {name}")
        if self.sim.estop:
            self.send("FaultList: Fault_EStopPressed estop")
        self.send("End of FaultsGet")

    def _cmd_applicationfaultset(self, args, line):
        if not args:
            self._error(line, "applicationFaultSet requires a name")
            return
        name = args[0]
        short = args[1] if len(args) > 1 else name
        fault_id = "Fault_Driving_Critical_Application"
        self.sim.app_faults[name] = (fault_id, short)
        self.send(f"ApplicationFaultSet set {name}")
        self.server.broadcast(f'Fault: {fault_id} {name} "{short}"')

    def _cmd_applicationfaultclear(self, args, line):
        if not args:
            self._error(line, "applicationFaultClear requires a name")
            return
        name = args[0]
        if name in self.sim.app_faults:
            del self.sim.app_faults[name]
            self.send(f"ApplicationFaultClear cleared {name}")
        else:
            self._error(line, f"No application fault '{name}'")

    def _cmd_applicationfaultquery(self, args, line):
        for name, (fault_id, _short) in self.sim.app_faults.items():
            self.send(f"ApplicationFaultQuery: {fault_id} {name}")
        self.send("End of ApplicationFaultQuery")

    # -- queuing (Fleet surface)

    def _parse_priority(self, token: str | None, line: str) -> int | None:
        if token is None or token.lower() == "default":
            return 10
        try:
            return int(token)
        except ValueError:
            self._error(line, f"Invalid priority '{token}'")
            return None

    def _cmd_queuepickup(self, args, line):
        if not args:
            self._error(line, "queuePickup requires a goal name")
            return
        goal = args[0]
        if goal not in self.sim.goals:
            self.send(f"CommandError: queuePickup {goal}")
            self.send(f"CommandErrorDescription: No goal '{goal}'")
            return
        priority = self._parse_priority(args[1] if len(args) > 1 else None, line)
        if priority is None:
            return
        job_id = args[2] if len(args) > 2 else None
        job = self.sim.queue_pickup(goal, priority, job_id)
        self.send(
            f'queuepickup goal "{goal}" with priority {priority}, id {job.item_id} '
            f"and job_id {job.job_id} successfully queued"
        )

    def _cmd_queuepickupdropoff(self, args, line):
        if len(args) < 2:
            self._error(line, "queuePickupDropoff requires pickup and dropoff goal names")
            return
        pickup_goal, dropoff_goal = args[0], args[1]
        for goal in (pickup_goal, dropoff_goal):
            if goal not in self.sim.goals:
                self.send(f"CommandError: queuePickupDropoff {goal}")
                self.send(f"CommandErrorDescription: No goal '{goal}'")
                return
        priority = self._parse_priority(args[2] if len(args) > 2 else None, line)
        if priority is None:
            return
        job_id = args[3] if len(args) > 3 else None
        pickup = self.sim.queue_pickup(pickup_goal, priority, job_id)
        dropoff = self.sim.queue_dropoff(
            dropoff_goal, priority, pickup.job_id, after=pickup.item_id
        )
        self.send(
            f'queuepickupdropoff goal "{pickup_goal}" and goal "{dropoff_goal}" with '
            f"priority {priority}, ids {pickup.item_id} and {dropoff.item_id} and "
            f"job_id {pickup.job_id} successfully queued"
        )

    _QUERY_TYPES = ("id", "jobid", "robotname", "status")

    def _cmd_queuequery(self, args, line):
        if len(args) < 2 or args[0].lower() not in self._QUERY_TYPES:
            self._error(line, "queueQuery requires <type: id|jobId|robotName|status> <value>")
            return
        kind, value = args[0].lower(), args[1]
        echo_string = args[2] if len(args) > 2 else "None"
        for job in self._match_jobs(kind, value):
            self.send(job.query_line(echo_string))
        self.send("EndQueueQuery")

    def _cmd_queueshow(self, args, line):
        for job in sorted(self.sim.jobs, key=lambda j: (-j.priority, j.queued_at)):
            self.send(job.query_line().replace("QueueQuery:", "QueueShow:", 1))
        self.send("EndQueueShow")

    def _cmd_queuecancel(self, args, line):
        if len(args) < 2 or args[0].lower() not in self._QUERY_TYPES:
            self._error(line, "queueCancel requires <type: id|jobId|robotName|status> <value>")
            return
        reason = args[3] if len(args) > 3 else None
        cancelled = self.sim.cancel(args[0].lower(), args[1], reason)
        self.send(f"queuecancel {args[0]} {args[1]} cancelled {len(cancelled)} item(s)")

    def _match_jobs(self, kind: str, value: str) -> list[Job]:
        return [
            j
            for j in self.sim.jobs
            if (kind == "id" and j.item_id == value)
            or (kind == "jobid" and j.job_id == value)
            or (kind == "robotname" and j.robot == value)
            or (kind == "status" and j.status.lower() == value.lower())
        ]

    # -- NON-STANDARD emulator controls

    def _cmd_emulator(self, args, line):
        sim = self.sim
        if not args:
            self._error(line, "emulator requires: battery|estop|teleport|timescale")
            return
        sub = args[0].lower()
        try:
            if sub == "battery":
                sim.battery = max(0.0, min(100.0, float(args[1])))
                self.send(f"Emulator: battery {sim.battery:.1f}")
            elif sub == "estop":
                sim.estop = args[1].lower() == "on"
                self.send(f"Emulator: estop {'on' if sim.estop else 'off'}")
            elif sub == "teleport":
                sim.x, sim.y, sim.heading = float(args[1]), float(args[2]), float(args[3])
                self.send(f"Emulator: teleport {sim.x:.0f} {sim.y:.0f} {sim.heading:.0f}")
            elif sub == "timescale":
                sim.set_time_scale(float(args[1]))
                self.send(f"Emulator: timescale {sim.time_scale}")
            else:
                self._error(line, f"Unknown emulator control '{sub}'")
        except (IndexError, ValueError):
            self._error(line, f"Bad arguments for emulator {sub}")
