"""Fleet-side VDA 5050 master: discover robots on the broker, talk to each.

``FleetMaster`` owns a single MQTT connection with wildcard subscriptions
over ``interfaceName/majorVersion/+/+/<topic>`` for everything a robot
publishes, so robots need no configuration on this side: they appear the
moment their (typically retained) ``connection`` message — or any other
message — arrives, and every robot is exposed as a :class:`RobotHandle`.

A handle carries the fleet-control half of the protocol for one robot:
schema-validated publishing (``order``/``instantActions``, hard-fail on our
own invalid output) with the per-topic ``headerId`` sequencing the spec
requires, plus awaitable views of everything the robot reports. Incoming
messages are validated too, but never dropped — a real master must keep
working against a slightly-off robot, so problems are recorded on
``RobotHandle.protocol_problems`` instead. Do not branch on an *absence* of
recorded problems to conclude a message is well-formed on 2.0.0: those
upstream schemas declare no required fields, so nearly anything passes —
key logic off field presence (as this module does), never off validation
verdicts.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Callable
from typing import Any

from vda5050_emulator.clock import SimClock
from vda5050_emulator.mqtt import MQTTClient
from vda5050_emulator.profiles import Profile
from vda5050_emulator.profiles import profile as get_profile
from vda5050_emulator.topics import ROBOT_PUBLISHES, TopicBase, parse_topic
from vda5050_emulator.validation import validation_errors

_BUCKETS = {name: name + "s" for name in ROBOT_PUBLISHES}  # topic -> attribute


class RobotHandle:
    """One discovered robot: its message history and a validated publisher."""

    def __init__(self, fleet: FleetMaster, topics: TopicBase) -> None:
        self._fleet = fleet
        self.topics = topics
        self.states: list[dict] = []
        self.connections: list[dict] = []
        self.factsheets: list[dict] = []
        self.visualizations: list[dict] = []
        self.protocol_problems: list[tuple[str, list[str]]] = []
        self._header_ids: dict[str, int] = {}
        self.new_message = asyncio.Event()

    @property
    def manufacturer(self) -> str:
        return self.topics.manufacturer

    @property
    def serial_number(self) -> str:
        return self.topics.serial_number

    @property
    def connection_state(self) -> str:
        """Last reported connectionState; empty until a connection message."""
        if not self.connections:
            return ""
        return str(self.connections[-1].get("connectionState", ""))

    @property
    def online(self) -> bool:
        return self.connection_state == "ONLINE"

    @property
    def state(self) -> dict | None:
        return self.states[-1] if self.states else None

    @property
    def factsheet(self) -> dict | None:
        return self.factsheets[-1] if self.factsheets else None

    # -------------------------------------------------------------- receiving

    def _record(self, name: str, doc: dict) -> None:
        problems = validation_errors(name, doc, tag=self._fleet.profile.version)
        if problems:
            self.protocol_problems.append((name, problems))
        getattr(self, _BUCKETS[name]).append(doc)
        self.new_message.set()

    async def next_message(
        self,
        bucket: str,
        predicate: Callable[[dict], bool] | None = None,
        *,
        timeout: float = 10.0,
        past: bool = True,
    ) -> dict:
        """Wait for (or find) a message in ``bucket`` matching ``predicate``."""
        messages: list[dict] = getattr(self, bucket)
        seen = 0 if past else len(messages)
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            while seen < len(messages):
                doc = messages[seen]
                seen += 1
                if predicate is None or predicate(doc):
                    return doc
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError(
                    f"{self.serial_number}: no {bucket} message matching predicate within "
                    f"{timeout}s ({len(messages)} seen)"
                )
            self.new_message.clear()
            try:
                await asyncio.wait_for(self.new_message.wait(), timeout=remaining)
            except TimeoutError:
                continue

    async def next_state(
        self,
        predicate: Callable[[dict], bool] | None = None,
        *,
        timeout: float = 10.0,
        past: bool = True,
    ) -> dict:
        if predicate is None and past and self.states:
            return self.states[-1]
        return await self.next_message("states", predicate, timeout=timeout, past=past)

    async def action_status(
        self, action_id: str, *, statuses: tuple[str, ...], timeout: float = 10.0
    ) -> dict:
        """Wait until ``action_id`` reaches one of ``statuses``; returns its entry."""

        def matching(state: dict) -> bool:
            return find_action(state, action_id, statuses) is not None

        state = await self.next_state(matching, timeout=timeout)
        found = find_action(state, action_id, statuses)
        assert found is not None
        return found

    # ------------------------------------------------------------- publishing

    def _with_header(self, body: dict, *, topic: str) -> dict:
        header_id = self._header_ids.get(topic, 0)
        self._header_ids[topic] = header_id + 1
        profile = self._fleet.profile
        return {
            "headerId": header_id,
            "timestamp": self._fleet.clock.now_iso(),
            "version": profile.version,
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            **body,
        }

    async def publish(self, topic: str, body: dict) -> dict:
        """Add the header, validate against the official schema, publish.

        Raises ``ValueError`` instead of publishing when our own message is
        schema-invalid — a master that emits garbage has a bug, and a crash
        here surfaces it in development instead of in a robot's log.
        """
        message = self._with_header(body, topic=topic)
        problems = validation_errors(topic, message, tag=self._fleet.profile.version)
        if problems:
            raise ValueError(f"refusing to publish invalid {topic} message: {problems[:3]}")
        await self._fleet.client.publish(self.topics.topic(topic), json.dumps(message).encode())
        return message

    async def send_order(self, order: dict) -> dict:
        """Publish an order body ({orderId, orderUpdateId, nodes, edges})."""
        return await self.publish("order", order)

    async def send_instant_action(
        self,
        action_type: str,
        *,
        blocking_type: str = "NONE",
        parameters: dict[str, Any] | None = None,
        action_id: str | None = None,
    ) -> str:
        action_id = action_id or f"ia-{uuid.uuid4().hex[:12]}"
        action: dict[str, Any] = {
            "actionId": action_id,
            "actionType": action_type,
            "blockingType": blocking_type,
        }
        if self._fleet.profile.version == "2.0.0":
            # The 2.0.0 instantActions schema names the type field actionName;
            # later versions use actionType everywhere.
            action["actionName"] = action_type
        if parameters:
            action["actionParameters"] = [
                {"key": key, "value": value} for key, value in parameters.items()
            ]
        await self.publish("instantActions", {"actions": [action]})
        return action_id

    async def cancel_order(self, *, timeout: float = 10.0) -> dict:
        """Send ``cancelOrder`` and await its verdict.

        The 3.0.0 prose calls cancelOrder a HARD action, but the official
        instantActions schema pins every instant action's blockingType to
        NONE — and the schema wins on the wire.
        """
        action_id = await self.send_instant_action("cancelOrder")
        return await self.action_status(action_id, statuses=("FINISHED", "FAILED"), timeout=timeout)


def find_action(state: dict, action_id: str, statuses: tuple[str, ...]) -> dict | None:
    """Find ``action_id`` in any of the state's action-state arrays.

    2.x keeps instant-action states in the shared ``actionStates`` array;
    3.0 splits ``instantActionStates`` (and ``zoneActionStates``) out.
    """
    for array in ("actionStates", "instantActionStates", "zoneActionStates"):
        for entry in state.get(array, []):
            if entry.get("actionId") == action_id and entry.get("actionStatus") in statuses:
                return entry
    return None


def errors_referencing(state: dict, order_id: str) -> list[dict]:
    """Errors whose errorReferences point at ``order_id``.

    Matching on references — never on the wire errorType alone — matters on
    2.x, where five distinct semantic rejections all share the errorType
    "orderError".
    """
    matches = []
    for error in state.get("errors", []):
        for ref in error.get("errorReferences", []):
            if ref.get("referenceKey") == "orderId" and ref.get("referenceValue") == order_id:
                matches.append(error)
                break
    return matches


class FleetMaster:
    """Discover and drive every VDA 5050 robot on a broker."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        version: str = "3.0.0",
        interface_name: str | None = None,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        clock: SimClock | None = None,
    ) -> None:
        self.profile: Profile = get_profile(version)
        self.clock = clock or SimClock()
        self.interface_name = interface_name or self.profile.interface_name
        self.client = MQTTClient(
            client_id or f"fleet-master-{uuid.uuid4().hex[:8]}",
            host,
            port,
            username=username,
            password=password,
        )
        self.robots: dict[tuple[str, str], RobotHandle] = {}
        self.new_robot = asyncio.Event()
        self._reader: asyncio.Task | None = None

    async def connect(self) -> None:
        await self.client.connect()
        prefix = f"{self.interface_name}/{self.profile.major}"
        for name in ROBOT_PUBLISHES:
            await self.client.subscribe(f"{prefix}/+/+/{name}")
        self._reader = asyncio.create_task(self._read_loop())

    async def disconnect(self) -> None:
        if self._reader is not None:
            self._reader.cancel()
        if self.client.connected:
            await self.client.disconnect()

    async def __aenter__(self) -> FleetMaster:
        await self.connect()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.disconnect()

    async def _read_loop(self) -> None:
        while True:
            message = await self.client.messages.get()
            parsed = parse_topic(message.topic)
            if parsed is None:
                continue
            base, name = parsed
            if name not in _BUCKETS:
                continue
            try:
                doc = json.loads(message.payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                # A robot publishing undecodable bytes is worth remembering
                # even though there is no document to store.
                handle = self._handle_for(base)
                handle.protocol_problems.append((name, ["payload is not valid JSON"]))
                continue
            if not isinstance(doc, dict):
                continue
            self._handle_for(base)._record(name, doc)

    def _handle_for(self, base: TopicBase) -> RobotHandle:
        key = (base.manufacturer, base.serial_number)
        handle = self.robots.get(key)
        if handle is None:
            handle = RobotHandle(self, base)
            self.robots[key] = handle
            self.new_robot.set()
        return handle

    def robot(self, serial_number: str, manufacturer: str | None = None) -> RobotHandle:
        """Look up a discovered robot by serial (and manufacturer if ambiguous)."""
        matches = [
            handle
            for (mfr, serial), handle in self.robots.items()
            if serial == serial_number and manufacturer in (None, mfr)
        ]
        if not matches:
            known = sorted(serial for _, serial in self.robots)
            raise KeyError(f"no robot {serial_number!r} discovered (known: {known})")
        if len(matches) > 1:
            makers = sorted(handle.manufacturer for handle in matches)
            raise KeyError(f"serial {serial_number!r} is ambiguous across {makers}")
        return matches[0]

    async def wait_for_robots(
        self,
        count: int = 1,
        *,
        online: bool = True,
        timeout: float = 10.0,
    ) -> list[RobotHandle]:
        """Wait until ``count`` robots are discovered (and, by default, ONLINE)."""
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            ready = [h for h in self.robots.values() if h.online or not online]
            if len(ready) >= count:
                return ready[:count]
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                states = {
                    f"{h.manufacturer}/{h.serial_number}": h.connection_state or "no connection"
                    for h in self.robots.values()
                }
                raise TimeoutError(
                    f"only {len(ready)}/{count} robots ready within {timeout}s: {states}"
                )
            self.new_robot.clear()
            # Clearing is safe with concurrent next_message() consumers: set()
            # already woke any registered waiter, and they re-scan their lists
            # rather than re-reading the flag. Without it, one permanently-set
            # event would turn this wait into a spin.
            for handle in self.robots.values():
                handle.new_message.clear()
            waiters = [asyncio.create_task(self.new_robot.wait())]
            waiters += [asyncio.create_task(h.new_message.wait()) for h in self.robots.values()]
            try:
                await asyncio.wait(waiters, timeout=remaining, return_when=asyncio.FIRST_COMPLETED)
            finally:
                for task in waiters:
                    task.cancel()
