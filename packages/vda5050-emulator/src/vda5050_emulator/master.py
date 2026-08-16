"""Fleet-control-side helper: drive a VDA 5050 robot from tests or scripts.

``MasterControl`` is the counterpart of the emulated robot — it publishes
``order``/``instantActions`` (and ``zoneSet``/``responses`` on 3.0) and
collects everything the robot publishes. It validates its own outgoing
messages against the official schemas (use ``publish_raw`` to send garbage on
purpose in adversarial tests) and offers ``next_state`` with a predicate so
tests can await exactly the state transition they mean.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Callable
from typing import Any

from .clock import SimClock
from .mqtt import MQTTClient
from .profiles import profile as get_profile
from .topics import TopicBase
from .validation import validation_errors


class MasterControl:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        manufacturer: str,
        serial_number: str,
        version: str = "3.0.0",
        interface_name: str | None = None,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        clock: SimClock | None = None,
    ) -> None:
        self.profile = get_profile(version)
        self.clock = clock or SimClock()
        self.topics = TopicBase(
            manufacturer=manufacturer,
            serial_number=serial_number,
            interface_name=interface_name or self.profile.interface_name,
            major_version=self.profile.major,
        )
        self.client = MQTTClient(
            client_id or f"master-{uuid.uuid4().hex[:8]}",
            host,
            port,
            username=username,
            password=password,
        )
        self._header_ids: dict[str, int] = {}
        self.states: list[dict] = []
        self.connections: list[dict] = []
        self.factsheets: list[dict] = []
        self.visualizations: list[dict] = []
        self._new_message = asyncio.Event()
        self._reader: asyncio.Task | None = None

    async def connect(self) -> None:
        await self.client.connect()
        for name in ("state", "connection", "factsheet", "visualization"):
            await self.client.subscribe(self.topics.topic(name))
        self._reader = asyncio.create_task(self._read_loop())

    async def disconnect(self) -> None:
        if self._reader is not None:
            self._reader.cancel()
        if self.client.connected:
            await self.client.disconnect()

    async def _read_loop(self) -> None:
        buckets = {
            "state": self.states,
            "connection": self.connections,
            "factsheet": self.factsheets,
            "visualization": self.visualizations,
        }
        while True:
            message = await self.client.messages.get()
            name = message.topic.rsplit("/", 1)[1]
            try:
                doc = json.loads(message.payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if name in buckets:
                buckets[name].append(doc)
                self._new_message.set()

    # ------------------------------------------------------------- publishing

    def _with_header(self, body: dict, *, topic: str) -> dict:
        header_id = self._header_ids.get(topic, 0)
        self._header_ids[topic] = header_id + 1
        return {
            "headerId": header_id,
            "timestamp": self.clock.now_iso(),
            "version": self.profile.version,
            "manufacturer": self.topics.manufacturer,
            "serialNumber": self.topics.serial_number,
            **body,
        }

    async def _publish(self, topic: str, body: dict) -> dict:
        message = self._with_header(body, topic=topic)
        problems = validation_errors(topic, message, tag=self.profile.version)
        if problems:
            raise ValueError(f"refusing to publish invalid {topic} message: {problems[:3]}")
        await self.client.publish(self.topics.topic(topic), json.dumps(message).encode())
        return message

    async def publish_raw(self, topic: str, payload: bytes | dict) -> None:
        """No validation, no header handling — for adversarial tests."""
        if isinstance(payload, dict):
            payload = json.dumps(payload).encode()
        await self.client.publish(self.topics.topic(topic), payload)

    async def send_order(
        self,
        nodes: list[dict],
        edges: list[dict],
        *,
        order_id: str,
        order_update_id: int = 0,
    ) -> dict:
        return await self._publish(
            "order",
            {
                "orderId": order_id,
                "orderUpdateId": order_update_id,
                "nodes": nodes,
                "edges": edges,
            },
        )

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
        if parameters:
            action["actionParameters"] = [
                {"key": key, "value": value} for key, value in parameters.items()
            ]
        await self._publish("instantActions", {"actions": [action]})
        return action_id

    async def send_zone_set(self, zone_set: dict) -> dict:
        return await self._publish("zoneSet", {"zoneSet": zone_set})

    async def respond(
        self, request_id: str, grant_type: str, *, lease_expiry: str | None = None
    ) -> dict:
        response: dict[str, Any] = {"requestId": request_id, "grantType": grant_type}
        if lease_expiry is not None:
            response["leaseExpiry"] = lease_expiry
        return await self._publish("responses", {"responses": [response]})

    # --------------------------------------------------------------- awaiting

    async def next_state(
        self,
        predicate: Callable[[dict], bool] | None = None,
        *,
        timeout: float = 10.0,
        past: bool = True,
    ) -> dict:
        """Wait for (or find) a state message matching ``predicate``."""
        seen = 0 if past else len(self.states)
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            while seen < len(self.states):
                state = self.states[seen]
                seen += 1
                if predicate is None or predicate(state):
                    return state
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError(
                    f"no state matching predicate within {timeout}s "
                    f"({len(self.states)} states seen)"
                )
            self._new_message.clear()
            try:
                await asyncio.wait_for(self._new_message.wait(), timeout=remaining)
            except TimeoutError:
                continue

    async def action_status(
        self, action_id: str, *, statuses: tuple[str, ...], timeout: float = 10.0
    ) -> dict:
        """Wait until the action reaches one of ``statuses``; returns its state."""

        def matching(state: dict) -> bool:
            return self._find_action(state, action_id, statuses) is not None

        state = await self.next_state(matching, timeout=timeout)
        found = self._find_action(state, action_id, statuses)
        assert found is not None
        return found

    @staticmethod
    def _find_action(state: dict, action_id: str, statuses: tuple[str, ...]) -> dict | None:
        arrays = ("actionStates", "instantActionStates", "zoneActionStates")
        for array in arrays:
            for entry in state.get(array, []):
                if entry.get("actionId") == action_id and entry.get("actionStatus") in statuses:
                    return entry
        return None


def make_node(
    node_id: str,
    sequence_id: int,
    *,
    released: bool = True,
    x: float | None = None,
    y: float | None = None,
    map_id: str = "map-0",
    theta: float | None = None,
    actions: list[dict] | None = None,
    deviation: float | None = None,
) -> dict:
    node: dict[str, Any] = {
        "nodeId": node_id,
        "sequenceId": sequence_id,
        "released": released,
        "actions": actions or [],
    }
    if x is not None and y is not None:
        position: dict[str, Any] = {"x": x, "y": y, "mapId": map_id}
        if theta is not None:
            position["theta"] = theta
        if deviation is not None:
            position["allowedDeviationXY"] = {"a": deviation, "b": deviation, "theta": 0.0}
        node["nodePosition"] = position
    return node


def make_edge(
    edge_id: str,
    sequence_id: int,
    *,
    released: bool = True,
    start_node_id: str = "",
    end_node_id: str = "",
    version: str = "3.0.0",
    length: float | None = None,
    maximum_speed: float | None = None,
    actions: list[dict] | None = None,
) -> dict:
    edge: dict[str, Any] = {
        "edgeId": edge_id,
        "sequenceId": sequence_id,
        "released": released,
        "actions": actions or [],
    }
    if version.startswith("2."):
        edge["startNodeId"] = start_node_id
        edge["endNodeId"] = end_node_id
    if length is not None:
        edge["length"] = length
    if maximum_speed is not None:
        edge["maximumSpeed"] = maximum_speed
    return edge


def make_action(
    action_type: str,
    *,
    blocking_type: str = "NONE",
    parameters: dict[str, Any] | None = None,
    action_id: str | None = None,
    retriable: bool | None = None,
) -> dict:
    action: dict[str, Any] = {
        "actionId": action_id or f"a-{uuid.uuid4().hex[:12]}",
        "actionType": action_type,
        "blockingType": blocking_type,
    }
    if parameters:
        action["actionParameters"] = [
            {"key": key, "value": value} for key, value in parameters.items()
        ]
    if retriable is not None:
        action["retriable"] = retriable
    return action
