"""A MassRobotics AMR Interop Standard receiver (fleet side).

The counterpart role to :class:`~massrobotics_emulator.robot.MassRoboticsAMR`
— a WebSocket server any certified robot (Vecna's fleet included) can be
pointed at. It validates every incoming message against the vendored
official schema and keeps a live registry of robots. Violations are
recorded per robot, never dropped, mirroring how the VDA 5050 master
handles protocol problems: absence of evidence should be inspectable.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field

from . import ws
from .validation import validation_errors


@dataclass
class RobotRecord:
    """Everything the receiver knows about one reporting robot."""

    uuid: str
    identity: dict | None = None
    statuses: list[dict] = field(default_factory=list)
    total_statuses: int = 0  # monotonic; statuses keeps only a bounded tail
    problems: list[tuple[str, list[str]]] = field(default_factory=list)
    connected: bool = True

    @property
    def latest(self) -> dict | None:
        return self.statuses[-1] if self.statuses else None


class InteropReceiver:
    """WebSocket server collecting identity/status reports from robots."""

    def __init__(self, *, host: str = "127.0.0.1", port: int = 0, keep_statuses: int = 500) -> None:
        self._server = ws.WSServer(self._handle, host=host, port=port)
        self._keep = keep_statuses
        self.robots: dict[str, RobotRecord] = {}
        self.rejected: list[tuple[str, list[str]]] = []  # not attributable to a uuid
        self._event = asyncio.Event()

    @property
    def port(self) -> int:
        return self._server.port

    @property
    def uri(self) -> str:
        return f"ws://127.0.0.1:{self.port}"

    async def start(self) -> None:
        await self._server.start()

    async def stop(self) -> None:
        await self._server.stop()

    # -- awaitables for tests and fleet logic ----------------------------

    async def wait_for_robots(self, count: int = 1, *, timeout: float = 10.0) -> list[RobotRecord]:
        """Until ``count`` robots have delivered a valid identityReport."""

        def ready() -> list[RobotRecord]:
            return [r for r in self.robots.values() if r.identity is not None]

        return await self._await(lambda: len(ready()) >= count and ready(), timeout, "robots")

    async def next_status(self, uuid: str, predicate=None, *, timeout: float = 10.0) -> dict:
        """The next (or a matching) statusReport from ``uuid``."""
        # Snapshot the monotonic counter, not a list index: the statuses
        # list keeps only a bounded tail, so indices go stale once trimmed.
        seen = self.robots[uuid].total_statuses if uuid in self.robots else 0

        def check() -> dict | None:
            record = self.robots.get(uuid)
            if record is None:
                return None
            fresh = min(record.total_statuses - seen, len(record.statuses))
            for status in record.statuses[-fresh:] if fresh > 0 else []:
                if predicate is None or predicate(status):
                    return status
            return None

        return await self._await(check, timeout, f"status from {uuid}")

    async def _await(self, check, timeout: float, what: str):
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            result = check()
            if result:
                return result
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError(f"no {what} within {timeout}s")
            self._event.clear()
            try:
                await asyncio.wait_for(self._event.wait(), remaining)
            except TimeoutError:
                continue

    # -- wire handling ---------------------------------------------------

    async def _handle(self, socket: ws.WebSocket, path: str) -> None:
        connection_uuid: str | None = None
        try:
            while True:
                raw = await socket.receive_text()
                connection_uuid = self._process(raw, connection_uuid)
                self._event.set()
        except ws.WSClosed:
            pass
        finally:
            if connection_uuid is not None and connection_uuid in self.robots:
                self.robots[connection_uuid].connected = False
                self._event.set()

    def _process(self, raw: str, connection_uuid: str | None) -> str | None:
        try:
            message = json.loads(raw)
        except json.JSONDecodeError as exc:
            self._record_problem(connection_uuid, "malformed JSON", [str(exc)])
            return connection_uuid
        if not isinstance(message, dict):
            self._record_problem(connection_uuid, "non-object message", [repr(message)[:100]])
            return connection_uuid

        uuid = message.get("uuid")
        is_identity = "manufacturerName" in message
        kind = "identityReport" if is_identity else "statusReport"
        problems = validation_errors(message, kind)

        if not isinstance(uuid, str):
            self._record_problem(connection_uuid, kind, problems or ["missing uuid"])
            return connection_uuid
        record = self.robots.setdefault(uuid, RobotRecord(uuid=uuid))
        record.connected = True
        if problems:
            record.problems.append((kind, problems))
            return uuid
        if is_identity:
            record.identity = message
        else:
            record.statuses.append(message)
            record.total_statuses += 1
            del record.statuses[: -self._keep]
        return uuid

    def _record_problem(self, uuid: str | None, kind: str, problems: list[str]) -> None:
        if uuid is not None and uuid in self.robots:
            self.robots[uuid].problems.append((kind, problems))
        else:
            self.rejected.append((kind, problems))
        self._event.set()
