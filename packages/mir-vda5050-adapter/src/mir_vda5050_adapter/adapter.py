"""VDA 5050 robot-side adapter for MiR robots.

The adapter is one MQTT client per MiR robot: it consumes ``order`` and
``instantActions``, translates released route nodes into a MiR mission
(positions + move actions + mission_queue), polls ``GET /status`` to track
execution, and publishes spec-valid ``state``/``connection``/``factsheet``
messages. Order acceptance reuses the vda5050-emulator's Figure-8 evaluator
(``vda5050_emulator.order.evaluate``) — validated against NVIDIA Isaac
Mission Dispatch and the InOrbit connector — so a MiR robot rejects and
accepts orders exactly like the emulated reference robot.

Deliberate scope (advertised honestly in the factsheet): route orders without
node/edge actions, plus the instant actions cancelOrder, startPause,
stopPause, stateRequest and factsheetRequest. Anything else is rejected with
the predefined error of the active protocol version.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import math
import uuid
from dataclasses import dataclass
from typing import Any

import httpx
from vda5050_emulator import factsheet as factsheet_mod
from vda5050_emulator import order as order_mod
from vda5050_emulator.errors import PREDEFINED, Clear, ErrorBoard, ErrorEntry
from vda5050_emulator.mqtt import Message, MQTTClient
from vda5050_emulator.profiles import _ERRORS_V3 as SEMANTIC_V3
from vda5050_emulator.profiles import Profile
from vda5050_emulator.profiles import profile as get_profile
from vda5050_emulator.topics import TopicBase
from vda5050_emulator.validation import validation_errors

from .mir import MiRClient

log = logging.getLogger(__name__)

_V2_LEVEL = {"WARNING": "WARNING", "URGENT": "WARNING", "CRITICAL": "FATAL", "FATAL": "FATAL"}

# MiR state_id (GET /status): 3 Ready, 4 Pause, 5 Executing.
MIR_READY, MIR_PAUSE, MIR_EXECUTING = 3, 4, 5

INSTANT_ACTIONS = ("cancelOrder", "startPause", "stopPause", "stateRequest", "factsheetRequest")


@dataclass
class AdapterConfig:
    mir_url: str = "http://127.0.0.1:8080"
    mir_username: str = "distributor"
    mir_password: str = "distributor"  # noqa: S105 — MiR factory default, same as mir-emulator
    manufacturer: str = "MiR"
    serial_number: str = "mir-robot-1"
    version: str = "2.0.0"  # VDA 5050 protocol version to speak
    interface_name: str | None = None
    poll_interval: float = 0.5  # seconds between GET /status polls
    node_deviation: float = 0.3  # meters: node counts as traversed inside this
    min_state_interval: float = 0.1
    state_interval: float = 5.0  # periodic state publish
    username: str | None = None  # MQTT credentials
    password: str | None = None


class MiRVDA5050Adapter:
    def __init__(
        self,
        config: AdapterConfig | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 1883,
        mir_transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.config = config or AdapterConfig()
        self.profile: Profile = get_profile(self.config.version)
        self.topics = TopicBase(
            manufacturer=self.config.manufacturer,
            serial_number=self.config.serial_number,
            interface_name=self.config.interface_name or self.profile.interface_name,
            major_version=self.profile.major,
        )
        self.mir = MiRClient(
            self.config.mir_url,
            username=self.config.mir_username,
            password=self.config.mir_password,
            transport=mir_transport,
        )
        self._header_ids: dict[str, int] = {}
        will_body = self._with_header(
            {"connectionState": self.profile.connection_broken}, topic="connection"
        )
        self.client = MQTTClient(
            f"mir-vda5050-{self.topics.serial_number}",
            host,
            port,
            username=self.config.username,
            password=self.config.password,
            will=Message(
                self.topics.topic("connection"),
                json.dumps(will_body).encode(),
                qos=1,
                retain=True,
            ),
        )

        # Live MiR view (updated by the poll loop).
        self.x = self.y = self.theta = 0.0
        self.map_id = ""
        self.battery = 100.0
        self.driving = False
        self.paused = False
        self.mir_errors: list[dict] = []

        # VDA order bookkeeping.
        self.order_id = ""
        self.order_update_id = 0
        self.has_order = False
        self.cancelled = False
        self.last_node_id = ""
        self.last_node_sequence_id = 0
        self._nodes: dict[int, dict] = {}
        self._pending: list[dict] = []  # released nodes not yet traversed, in order
        self.node_states: list[dict] = []
        self.edge_states: list[dict] = []
        self.action_states: list[dict] = []
        self.instant_action_states: list[dict] = []
        self._known_instant_ids: set[str] = set()
        self._last_order_digest = ""
        self._queue_entry_id: int | None = None

        self.errors = ErrorBoard()
        self._state_dirty = asyncio.Event()
        self._last_state_time = 0.0
        self._tasks: list[asyncio.Task] = []

    # ------------------------------------------------------------------ MQTT

    def _with_header(self, body: dict, *, topic: str) -> dict:
        header_id = self._header_ids.get(topic, 0)
        self._header_ids[topic] = header_id + 1
        import time

        from vda5050_emulator.clock import iso

        return {
            "headerId": header_id,
            "timestamp": iso(time.time()),
            "version": self.profile.version,
            "manufacturer": self.topics.manufacturer,
            "serialNumber": self.topics.serial_number,
            **body,
        }

    async def _publish(self, topic: str, body: dict, *, qos: int = 0, retain: bool = False):
        message = self._with_header(body, topic=topic)
        problems = validation_errors(topic, message, tag=self.profile.version)
        if problems:
            raise RuntimeError(f"adapter produced an invalid {topic} message: {problems[:3]}")
        await self.client.publish(
            self.topics.topic(topic), json.dumps(message).encode(), qos=qos, retain=retain
        )
        return message

    async def start(self) -> None:
        status = await self.mir.status()
        self._ingest_status(status)
        await self.client.connect()
        await self._publish("connection", {"connectionState": "ONLINE"}, qos=1, retain=True)
        await self.publish_factsheet()
        for name in ("order", "instantActions"):
            await self.client.subscribe(self.topics.topic(name))
        await self.publish_state()
        self._tasks = [
            asyncio.create_task(self._poll_loop()),
            asyncio.create_task(self._inbound_loop()),
            asyncio.create_task(self._state_loop()),
        ]

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task
        if self.client.connected:
            with contextlib.suppress(Exception):
                await self._publish(
                    "connection", {"connectionState": "OFFLINE"}, qos=1, retain=True
                )
            await self.client.disconnect()
        await self.mir.close()

    # ------------------------------------------------------------- MiR side

    def _ingest_status(self, status: dict) -> None:
        """Fold one GET /status document into the adapter's view.

        Defensive on purpose: a real MiR under upgrade/fault can return
        partial or malformed fields, and a single bad document must neither
        kill the poll loop nor leak non-finite numbers into published state
        (json.dumps would emit literal NaN — invalid JSON on the wire).
        Unusable fields keep their previous value.
        """
        if not isinstance(status, dict):
            return
        position = status.get("position")
        position = position if isinstance(position, dict) else {}
        self.x = _finite(position.get("x"), self.x)
        self.y = _finite(position.get("y"), self.y)
        orientation = _finite(position.get("orientation"), math.degrees(self.theta))
        self.theta = math.radians(orientation)
        map_id = status.get("map_id")
        if isinstance(map_id, str) and map_id:
            self.map_id = map_id
        self.battery = min(100.0, max(0.0, _finite(status.get("battery_percentage"), self.battery)))
        try:
            state_id = int(status.get("state_id", MIR_READY))
        except (TypeError, ValueError):
            state_id = MIR_READY
        driving = state_id == MIR_EXECUTING
        paused = state_id == MIR_PAUSE
        if driving != self.driving or paused != self.paused:
            self.touch()
        self.driving, self.paused = driving, paused
        errors = status.get("errors")
        self.mir_errors = (
            [e for e in errors if isinstance(e, dict)] if isinstance(errors, list) else []
        )

    async def _poll_loop(self) -> None:
        while True:
            await asyncio.sleep(self.config.poll_interval)
            try:
                status = await self.mir.status()
            except (httpx.HTTPError, OSError, ValueError):
                # ValueError covers a MiR answering 200 with a non-JSON body
                # (reverse-proxy error pages during robot reboots do this).
                self._report(
                    "not_available",
                    {},
                    "MiR REST API unreachable",
                    condition_key="mir-unreachable",
                )
                continue
            # Clear ONLY the unreachable error. On 2.x several semantic errors
            # share the wire name "orderError", so clearing by type alone here
            # raced order-rejection reports away before a state publish could
            # capture them (the source of the intermittent CI failure).
            self.errors.clear_condition(self.profile.error_type("not_available"), "mir-unreachable")
            self._ingest_status(status)
            self._advance_traversal()
            await self._check_completion()

    def _advance_traversal(self) -> None:
        """Mark pending nodes as traversed from the polled MiR pose.

        MiR executes move actions strictly in order, so being inside the
        deviation window of a LATER pending node implies every earlier node
        was traversed. That monotonicity makes pose sampling safe: a poll of
        only the head node can miss a waypoint whose deviation window is
        narrower than one poll interval's travel distance.
        """
        reached = -1
        for index, node in enumerate(self._pending):
            position = node.get("nodePosition")
            if not isinstance(position, dict):
                continue
            if math.dist(
                (self.x, self.y), (float(position["x"]), float(position["y"]))
            ) <= self._deviation_of(node):
                reached = index
        if reached < 0:
            return
        for node in self._pending[: reached + 1]:
            self._mark_traversed(node)
        del self._pending[: reached + 1]
        self.touch()

    def _mark_traversed(self, node: dict) -> None:
        self.last_node_id = node["nodeId"]
        self.last_node_sequence_id = node["sequenceId"]
        self.node_states = [n for n in self.node_states if n["sequenceId"] != node["sequenceId"]]
        self.edge_states = [e for e in self.edge_states if e["sequenceId"] >= node["sequenceId"]]

    def _deviation_of(self, node: dict) -> float:
        deviation = (node.get("nodePosition") or {}).get("allowedDeviationXY")
        if isinstance(deviation, int | float) and deviation > 0:
            return float(deviation)
        if isinstance(deviation, dict):
            return max(float(deviation.get("a", 0.0)), 0.05)
        return self.config.node_deviation

    async def _check_completion(self) -> None:
        if self._queue_entry_id is None:
            return
        try:
            entry = await self.mir.queue_entry(self._queue_entry_id)
        except httpx.HTTPError:
            return
        if entry.get("state") == "Done":
            # MiR finished every move action, so all remaining released nodes
            # were reached even if pose sampling missed their windows.
            for node in self._pending:
                self._mark_traversed(node)
            self._pending = []
            self._queue_entry_id = None
            self.touch()
        elif entry.get("state") == "Aborted":
            self._queue_entry_id = None
            self.touch()

    # ------------------------------------------------------------- VDA side

    async def _inbound_loop(self) -> None:
        while True:
            message = await self.client.messages.get()
            name = message.topic.rsplit("/", 1)[1]
            log.debug("adapter dispatching inbound %r", name)
            try:
                doc = json.loads(message.payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._report("validation", {"topic": name}, "message is not valid JSON")
                continue
            try:
                if name == "order":
                    await self._on_order(doc)
                elif name == "instantActions":
                    await self._on_instant_actions(doc)
            except Exception as exc:  # one bad message must never kill the adapter,
                # but a swallowed exception must still be observable: it
                # surfaces as a WARNING in the state's errors array.
                self._report("validation", {"topic": name}, f"internal error: {exc!r}")
                continue

    def _situation(self) -> order_mod.Situation:
        decision_point = None
        base = [n for n in self._nodes.values() if n["released"]]
        if base:
            last = max(base, key=lambda n: n["sequenceId"])
            decision_point = (last["nodeId"], last["sequenceId"])
        return order_mod.Situation(
            order_id=self.order_id,
            order_update_id=self.order_update_id,
            has_order=self.has_order,
            idle=self.is_idle(),
            cancelled=self.cancelled,
            decision_point=decision_point,
            position=(self.x, self.y),
            theta=self.theta,
            last_node_id=self.last_node_id,
            map_id=self.map_id,
            known_maps=frozenset({self.map_id, ""}),
            supported_actions=frozenset(INSTANT_ACTIONS),
            supported_node_actions=frozenset(),
            supported_edge_actions=frozenset(),
            accepts_orders=not self.errors.fatal,
            edges_carry_node_ids=self.profile.edges_carry_node_ids,
        )

    def is_idle(self) -> bool:
        settled = all(a["actionStatus"] in ("FINISHED", "FAILED") for a in self.action_states)
        return not self.node_states and not self.edge_states and settled

    async def _on_order(self, doc: dict) -> None:
        problems = validation_errors("order", doc, tag=self.profile.version)
        log.debug("order schema problems: %d", len(problems))
        if problems:
            self._report(
                "validation",
                {"topic": "order", "orderId": str(doc.get("orderId", ""))},
                f"schema violations: {problems[:3]}",
            )
            return
        decision = order_mod.evaluate(doc, self._situation())
        log.debug(
            "order %r verdict=%s key=%s detail=%r",
            doc.get("orderId"),
            decision.verdict,
            decision.error_key,
            decision.detail,
        )
        if decision.verdict == "ignore":
            if _digest(doc) != self._last_order_digest:
                self._report(
                    "same_order_update",
                    {"orderId": doc["orderId"]},
                    "same orderUpdateId with different content",
                )
            return
        if decision.verdict == "reject":
            self._report(decision.error_key, decision.references, decision.detail)
            return
        await self._accept(doc, decision)

    async def _accept(self, doc: dict, decision: order_mod.Decision) -> None:
        self.errors.clear_for(Clear.NEW_ORDER)
        self._last_order_digest = _digest(doc)
        new_nodes = [
            n
            for n in doc["nodes"]
            if decision.is_update is False or n["sequenceId"] > decision.append_from
        ]
        if not decision.is_update:
            self._nodes = {n["sequenceId"]: n for n in doc["nodes"]}
            self.node_states = [_node_state(n, self.profile.version) for n in doc["nodes"][1:]]
            self.edge_states = [_edge_state(e) for e in doc["edges"]]
            self.action_states = []
            first = doc["nodes"][0]
            self.last_node_id = first["nodeId"]
            self.last_node_sequence_id = first["sequenceId"]
            self._pending = [n for n in doc["nodes"][1:] if n["released"]]
        else:
            for node in new_nodes:
                self._nodes[node["sequenceId"]] = node
                self.node_states.append(_node_state(node, self.profile.version))
                if node["released"]:
                    self._pending.append(node)
            for edge in doc["edges"]:
                if edge["sequenceId"] > decision.append_from:
                    self.edge_states.append(_edge_state(edge))
        self.order_id = doc["orderId"]
        self.order_update_id = doc["orderUpdateId"]
        self.has_order = True
        self.cancelled = False
        waypoints = [
            n["nodePosition"] | {"theta": n["nodePosition"].get("theta")}
            for n in (doc["nodes"] if not decision.is_update else new_nodes)
            if n["released"] and isinstance(n.get("nodePosition"), dict)
        ]
        # The first node of a fresh order is where the robot already stands.
        if not decision.is_update and waypoints:
            waypoints = waypoints[1:]
        if waypoints:
            try:
                self._queue_entry_id = await self.mir.enqueue_route(
                    f"vda-{doc['orderId']}-u{doc['orderUpdateId']}", waypoints, self.map_id
                )
            except (httpx.HTTPError, OSError, ValueError, KeyError) as exc:
                # MiR died mid-translation (possibly after creating some
                # positions/actions). Without this rollback the adapter kept a
                # phantom active order with no mission behind it, rejecting
                # every subsequent order with OTHER_ORDER_ACTIVE until a
                # manual cancel. Abort observably instead: back to idle
                # (ids kept, per 6.6.7 spirit) with the failure reported.
                self.node_states = []
                self.edge_states = []
                self._pending = []
                self._queue_entry_id = None
                # NEW_ORDER retention (Table 9 style: until the next order
                # is accepted) — not_available's default CONDITION retention
                # would leave this error stranded forever.
                self._report(
                    "not_available",
                    {"orderId": doc["orderId"]},
                    f"order aborted: MiR mission enqueue failed ({exc!r})",
                    clear=Clear.NEW_ORDER,
                )
        self.touch()

    # -- instant actions ----------------------------------------------------

    async def _on_instant_actions(self, doc: dict) -> None:
        problems = validation_errors("instantActions", doc, tag=self.profile.version)
        actions = doc.get("actions")
        if problems:
            self._report(
                "validation", {"topic": "instantActions"}, f"schema violations: {problems[:3]}"
            )
        # Same 1.x compatibility as the emulator (proven needed by Isaac
        # Mission Dispatch): execute an `instantActions`-shaped array even
        # when the (vacuous) 2.0.0 schema raises no objection.
        if not isinstance(actions, list):
            actions = doc.get("instantActions")
            if not isinstance(actions, list):
                return
        self.errors.clear_for(Clear.NEW_INSTANT_ACTION)
        for action in actions or []:
            if isinstance(action, dict):
                await self._run_instant(action)

    async def _run_instant(self, action: dict) -> None:
        action_type = action.get("actionType") or action.get("actionName") or ""
        action_id = action.get("actionId") or f"instant-{uuid.uuid4().hex[:10]}"
        if action_id in self._known_instant_ids:
            return  # idempotent redelivery
        self._known_instant_ids.add(action_id)
        state = {"actionId": action_id, "actionStatus": "RUNNING", "actionType": action_type}
        self.instant_action_states.append(state)
        try:
            if action_type == "cancelOrder":
                await self._cancel_order(state, action)
            elif action_type == "startPause":
                await self.mir.set_state(MIR_PAUSE)
                state["actionStatus"] = "FINISHED"
            elif action_type == "stopPause":
                await self.mir.set_state(MIR_READY)
                state["actionStatus"] = "FINISHED"
            elif action_type == "stateRequest":
                state["actionStatus"] = "FINISHED"
                await self.publish_state()
            elif action_type == "factsheetRequest":
                await self.publish_factsheet()
                state["actionStatus"] = "FINISHED"
            else:
                state["actionStatus"] = "FAILED"
                self._report(
                    "invalid_instant_action",
                    {"actionId": action_id},
                    f"unsupported instant action {action_type!r}",
                )
        except httpx.HTTPError as exc:
            state["actionStatus"] = "FAILED"
            state["actionResult"] = f"MiR API error: {exc}"
        self.touch()

    async def _cancel_order(self, state: dict, action: dict) -> None:
        parameters = {p.get("key"): p.get("value") for p in action.get("actionParameters", [])}
        requested = parameters.get("orderId")
        if (
            self.is_idle()
            or self.cancelled
            or (requested is not None and str(requested) != self.order_id)
        ):
            state["actionStatus"] = "FAILED"
            self._report("no_order_to_cancel", {"actionId": state["actionId"]}, "no active order")
            return
        await self.mir.clear_mission_queue()
        self.cancelled = True
        self._pending = []
        self._queue_entry_id = None
        self.node_states = []
        self.edge_states = []
        for entry in self.action_states:
            if entry["actionStatus"] not in ("FINISHED", "FAILED"):
                entry["actionStatus"] = "FAILED"
        state["actionStatus"] = "FINISHED"

    # ------------------------------------------------------------ publishing

    def touch(self) -> None:
        self._state_dirty.set()

    async def _state_loop(self) -> None:
        while True:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._state_dirty.wait(), timeout=self.config.state_interval)
            self._state_dirty.clear()
            loop_time = asyncio.get_running_loop().time()
            wait = self.config.min_state_interval - (loop_time - self._last_state_time)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_state_time = asyncio.get_running_loop().time()
            with contextlib.suppress(Exception):
                await self.publish_state()

    def state_body(self) -> dict:
        profile = self.profile
        body: dict[str, Any] = {
            "orderId": self.order_id,
            "orderUpdateId": self.order_update_id,
            "lastNodeId": self.last_node_id,
            "lastNodeSequenceId": self.last_node_sequence_id,
            "nodeStates": [dict(n) for n in self.node_states],
            "edgeStates": [dict(e) for e in self.edge_states],
            "driving": self.driving,
            "paused": self.paused,
            "operatingMode": "AUTOMATIC",
            "errors": self._wire_errors(),
            "information": [],
            "safetyState": {profile.estop_field: "NONE", "fieldViolation": False},
            profile.position_field: {
                "x": round(self.x, 6),
                "y": round(self.y, 6),
                "theta": round(self.theta, 6),
                "mapId": self.map_id,
                profile.localized_field: True,
            },
            "velocity": {"vx": 0.0, "vy": 0.0, "omega": 0.0},
            profile.battery_field: {
                profile.charge_field: self.battery,
                "charging": False,
            },
            "actionStates": [dict(a) for a in self.action_states],
        }
        if profile.has_instant_action_states:
            body["instantActionStates"] = [dict(a) for a in self.instant_action_states]
        else:
            body["actionStates"] += [dict(a) for a in self.instant_action_states]
        if profile.has_maps:
            body["maps"] = [{"mapId": self.map_id, "mapVersion": "1", "mapStatus": "ENABLED"}]
        if profile.has_zones:
            body["zoneSets"] = []
            body["zoneActionStates"] = []
            body["zoneRequests"] = []
            body["edgeRequests"] = []
        return body

    def _wire_errors(self) -> list[dict]:
        docs = []
        for doc in self.errors.as_json():
            if self.profile.version.startswith("2."):
                doc["errorLevel"] = _V2_LEVEL[doc["errorLevel"]]
            docs.append(doc)
        for mir_error in self.mir_errors:
            if not mir_error.get("code"):
                continue  # code 0 = healthy; the mir-emulator seeds one such sample entry
            docs.append(
                {
                    "errorType": "mirError",
                    "errorLevel": "WARNING",
                    "errorDescription": str(mir_error.get("description", mir_error))[:200],
                }
            )
        return docs

    async def publish_state(self) -> None:
        await self._publish("state", self.state_body())

    async def publish_factsheet(self) -> None:
        shim = _FactsheetShim(self.config)
        body = factsheet_mod.build_factsheet(shim, self.profile)
        key = "mobileRobotActions" if not self.profile.version.startswith("2.") else "agvActions"
        body["protocolFeatures"][key] = [
            entry
            for entry in body["protocolFeatures"][key]
            if entry["actionType"] in INSTANT_ACTIONS
        ]
        await self._publish("factsheet", body, retain=True)

    def _report(
        self,
        key: str,
        references: dict,
        detail: str = "",
        *,
        condition_key: str = "",
        clear: Clear | None = None,
    ) -> None:
        if key not in self.profile.error_names:
            return
        level, default_clear = PREDEFINED.get(SEMANTIC_V3[key], ("WARNING", Clear.NEW_ORDER))
        self.errors.report(
            ErrorEntry(
                error_type=self.profile.error_type(key),
                references={k: str(v) for k, v in references.items()},
                description=detail,
                level=level,
                clear=clear or default_clear,
                condition_key=condition_key,
            )
        )
        self.touch()


class _FactsheetShim:
    """Just the config attributes the emulator's factsheet builder reads."""

    def __init__(self, config: AdapterConfig) -> None:
        self.series_name = "MiR-VDA5050"
        self.max_speed = 1.5
        self.min_state_interval = config.min_state_interval
        self.default_state_interval = config.state_interval
        self.visualization_interval = 0
        self.software_version = "mir-vda5050-adapter"


def _finite(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) else fallback


def _digest(doc: dict) -> str:
    return json.dumps(
        {k: v for k, v in doc.items() if k not in ("headerId", "timestamp")}, sort_keys=True
    )


def _node_state(node: dict, version: str) -> dict:
    state = {
        "nodeId": node["nodeId"],
        "sequenceId": node["sequenceId"],
        "released": bool(node["released"]),
    }
    position = node.get("nodePosition")
    if isinstance(position, dict) and (version != "2.0.0" or "theta" in position):
        state["nodePosition"] = position
    return state


def _edge_state(edge: dict) -> dict:
    return {
        "edgeId": edge["edgeId"],
        "sequenceId": edge["sequenceId"],
        "released": bool(edge["released"]),
    }
