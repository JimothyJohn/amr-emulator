"""The virtual mobile robot: one MQTT client speaking VDA 5050.

One ``VirtualAGV`` is one robot on the broker: it subscribes to
``order``/``instantActions`` (plus ``zoneSet``/``responses`` on 3.0 and the
emulator's own ``_emulator`` control topic), publishes ``state``,
``connection`` (retained, QoS 1, with a CONNECTION_BROKEN last will),
``factsheet`` (retained) and ``visualization``, and simulates order execution
on simulated time (clock.py).

Everything observable follows the recommendation: the acceptance flow of
Figure 8 (order.py), the action blocking rules of Figure 11 (actions.py), the
state-event publishing rules of 6.6, the error retention rules of Table 9
(errors.py) and the zone/request mechanics of 6.4/6.9 (zones.py). Everything
deliberately *not* standard lives behind the ``_emulator`` topic and the
Python fault-injection API, mirroring the MiR emulator's ``/_emulator``
endpoints: emergency stop, field violation, localization loss, battery
override, teleport, operating-mode switch, forced action failures, connection
drop and time scaling.
"""

from __future__ import annotations

import asyncio
import contextlib
import itertools
import json
import math
import uuid
from dataclasses import dataclass
from typing import Any

from . import factsheet as factsheet_mod
from . import order as order_mod
from .actions import ActionEngine, ActionRun, params
from .clock import SimClock
from .errors import PREDEFINED, Clear, ErrorBoard, ErrorEntry
from .mqtt import Message, MQTTClient
from .profiles import _ERRORS_V3 as SEMANTIC_V3
from .profiles import Profile
from .profiles import profile as get_profile
from .topics import EMULATOR_TOPIC, TopicBase
from .validation import validation_errors

_V2_LEVEL = {"WARNING": "WARNING", "URGENT": "WARNING", "CRITICAL": "FATAL", "FATAL": "FATAL"}


@dataclass
class AGVConfig:
    manufacturer: str = "amr-emulator"
    serial_number: str = "vagv-0001"
    version: str = "3.0.0"  # VDA 5050 protocol version: 2.0.0 | 2.1.0 | 3.0.0
    interface_name: str | None = None  # default: profile's customary name
    map_id: str = "map-0"
    map_version: str = "1"
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    default_speed: float = 1.0  # m/s when the order gives no limit
    max_speed: float = 1.5
    battery: float = 100.0
    driving_drain: float = 0.005  # % per simulated second while driving
    idle_drain: float = 0.0005
    charge_rate: float = 0.1
    action_duration: float = 2.0  # simulated seconds for generic actions
    pick_duration: float = 4.0
    drop_duration: float = 3.0
    download_duration: float = 3.0
    min_state_interval: float = 0.1  # simulated seconds between state messages
    default_state_interval: float = 30.0  # periodic state publish
    visualization_interval: float = 1.0  # 0 disables the topic
    series_name: str = "VAGV-EMU"
    software_version: str = "emulator"
    username: str | None = None
    password: str | None = None


class VirtualAGV:
    def __init__(
        self,
        config: AGVConfig | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 1883,
        clock: SimClock | None = None,
    ) -> None:
        self.config = config or AGVConfig()
        self.profile: Profile = get_profile(self.config.version)
        self.clock = clock or SimClock()
        self.topics = TopicBase(
            manufacturer=self.config.manufacturer,
            serial_number=self.config.serial_number,
            interface_name=self.config.interface_name or self.profile.interface_name,
            major_version=self.profile.major,
        )
        self._header_ids: dict[str, int] = {}
        will_body = self._with_header(
            {"connectionState": self.profile.connection_broken}, topic="connection"
        )
        self.client = MQTTClient(
            f"{self.topics.manufacturer}-{self.topics.serial_number}",
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

        # -- simulation state
        self.x, self.y, self.theta = self.config.x, self.config.y, self.config.theta
        self.map_id = self.config.map_id
        self.velocity = (0.0, 0.0, 0.0)
        self.driving = False
        self.paused = False
        self.localized = True
        self.emergency_stop = "NONE"
        self.field_violation = False
        self.operating_mode = "AUTOMATIC"
        self.loads: list[dict] = []
        self.distance_since_last_node = 0.0
        self.new_base_request = False
        self.hibernating = False
        self.connection_state = "OFFLINE"
        self.maps: list[dict] = (
            [
                {
                    "mapId": self.config.map_id,
                    "mapVersion": self.config.map_version,
                    "mapStatus": "ENABLED",
                }
            ]
            if self.profile.has_maps
            else []
        )
        self._battery_anchor = (self.config.battery, self.clock.time())
        self.charging = False

        # -- order state
        self.order_id = ""
        self.order_update_id = 0
        self.has_order = False
        self.cancelled = False
        self.last_node_id = ""
        self.last_node_sequence_id = 0
        self._nodes: dict[int, dict] = {}  # sequenceId -> node
        self._edges: dict[int, dict] = {}
        self.node_states: list[dict] = []
        self.edge_states: list[dict] = []
        self.action_states: list[dict] = []
        self.instant_action_states: list[dict] = []
        self.zone_action_states: list[dict] = []
        self.edge_requests: list[dict] = []
        self._last_order_digest: str = ""
        self._runs: dict[str, ActionRun] = {}

        self.errors = ErrorBoard()
        self.engine = ActionEngine(self)
        from .zones import ZoneBook, ZoneMembership

        self.zones = ZoneBook()
        self._zone_membership = ZoneMembership()
        self.forced_action_failures: dict[str, str] = {}

        self._last_state_header = 0
        self._state_dirty = asyncio.Event()
        self._situation_changed = asyncio.Event()
        self._driver_wake = asyncio.Event()
        self._tasks: list[asyncio.Task] = []
        self._stopping = False
        self._last_state_time = -math.inf
        self._wake_task: asyncio.Task | None = None

    # ------------------------------------------------------------------ MQTT

    async def start(self) -> None:
        await self.client.connect()
        self.connection_state = "ONLINE"
        await self._publish("connection", {"connectionState": "ONLINE"}, qos=1, retain=True)
        await self.publish_factsheet()
        for topic_filter in self.topics.subscription_filters():
            name = topic_filter.rsplit("/", 1)[1]
            if name in (*self.profile.subscribed_topics, EMULATOR_TOPIC):
                await self.client.subscribe(topic_filter)
        await self.publish_state(reason="startup")
        self._tasks = [
            asyncio.create_task(self._inbound_loop()),
            asyncio.create_task(self._state_loop()),
            asyncio.create_task(self._driver_loop()),
        ]
        if self.config.visualization_interval > 0:
            self._tasks.append(asyncio.create_task(self._visualization_loop()))

    async def stop(self) -> None:
        """Graceful shutdown: OFFLINE retained, clean MQTT disconnect."""
        self._stopping = True
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
        self.connection_state = "OFFLINE"

    async def drop_connection(self) -> None:
        """Abrupt connection loss: the broker publishes the last will."""
        await self.client.drop()

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

    async def _publish(self, topic: str, body: dict, *, qos: int = 0, retain: bool = False) -> dict:
        message = self._with_header(body, topic=topic)
        problems = validation_errors_for(self.profile.version, topic, message)
        if problems:
            raise RuntimeError(f"emulator produced an invalid {topic} message: {problems[:3]}")
        await self.client.publish(
            self.topics.topic(topic), json.dumps(message).encode(), qos=qos, retain=retain
        )
        return message

    # ------------------------------------------------------------- publishing

    async def publish_state(self, reason: str = "") -> None:
        if self.hibernating and reason != "hibernation":
            return
        message = await self._publish("state", self.state_body())
        self._last_state_header = message["headerId"]
        self._last_state_time = self.clock.time()

    async def publish_factsheet(self) -> None:
        body = factsheet_mod.build_factsheet(self.config, self.profile)
        await self._publish("factsheet", body, retain=True)

    def touch(self, _reason: str = "") -> None:
        """An observable state change happened -> schedule a state publish."""
        self._state_dirty.set()
        self._situation_changed.set()
        self._driver_wake.set()

    async def _state_loop(self) -> None:
        while True:
            try:
                await asyncio.wait_for(
                    self._state_dirty.wait(),
                    timeout=self.config.default_state_interval / self.clock.scale,
                )
                dirty = True
            except TimeoutError:
                dirty = False
            self._state_dirty.clear()
            if dirty:
                elapsed = self.clock.time() - self._last_state_time
                if elapsed < self.config.min_state_interval:
                    await self.clock.sleep(self.config.min_state_interval - elapsed)
                self._state_dirty.clear()
            if not self.hibernating:
                await self.publish_state(reason="event" if dirty else "interval")

    async def _visualization_loop(self) -> None:
        while True:
            await self.clock.sleep(self.config.visualization_interval)
            if self.hibernating or not self.client.connected:
                continue
            body: dict[str, Any] = {
                self.profile.position_field: self._position_doc(),
                "velocity": self._velocity_doc(),
            }
            if self.profile.has_zones:  # 3.0 requires the state back-reference
                body["referenceStateHeaderId"] = self._last_state_header
            with contextlib.suppress(Exception):
                await self._publish("visualization", body)

    # ------------------------------------------------------------- state body

    def _position_doc(self) -> dict:
        return {
            "x": round(self.x, 6),
            "y": round(self.y, 6),
            "theta": round(self.theta, 6),
            "mapId": self.map_id,
            self.profile.localized_field: self.localized,
        }

    def _velocity_doc(self) -> dict:
        vx, vy, omega = self.velocity
        return {"vx": vx, "vy": vy, "omega": omega}

    def battery_level(self) -> float:
        level, anchor = self._battery_anchor
        elapsed = max(0.0, self.clock.time() - anchor)
        if self.charging:
            level = min(100.0, level + self.config.charge_rate * elapsed)
        else:
            drain = self.config.driving_drain if self.driving else self.config.idle_drain
            level = max(0.0, level - drain * elapsed)
        return round(level, 3)

    def _reanchor_battery(self, level: float | None = None) -> None:
        self._battery_anchor = (
            self.battery_level() if level is None else level,
            self.clock.time(),
        )

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
            "newBaseRequest": self.new_base_request,
            "distanceSinceLastNode": round(self.distance_since_last_node, 6),
            "actionStates": [dict(a) for a in self.action_states],
            "operatingMode": self._wire_operating_mode(),
            "errors": self._wire_errors(),
            "information": [],
            "safetyState": {
                profile.estop_field: self.emergency_stop,
                "fieldViolation": self.field_violation,
            },
            profile.position_field: self._position_doc(),
            "velocity": self._velocity_doc(),
            profile.battery_field: {
                profile.charge_field: self.battery_level(),
                "charging": self.charging,
            },
        }
        if self.loads:
            body["loads"] = [dict(load) for load in self.loads]
        if profile.has_maps:
            body["maps"] = [dict(m) for m in self.maps]
        if profile.has_instant_action_states:
            body["instantActionStates"] = [dict(a) for a in self.instant_action_states]
        else:
            body["actionStates"] = body["actionStates"] + [
                dict(a) for a in self.instant_action_states
            ]
        if profile.has_zones:
            body["zoneSets"] = self.zones.state_entries()
            body["zoneActionStates"] = [dict(a) for a in self.zone_action_states]
            body["zoneRequests"] = [dict(r) for r in self.zones.zone_requests]
            body["edgeRequests"] = [dict(r) for r in self.edge_requests]
        return body

    def _wire_operating_mode(self) -> str:
        if self.operating_mode == "TEACH_IN":
            return self.profile.teach_in_mode
        return self.operating_mode

    def _wire_errors(self) -> list[dict]:
        wire = []
        for doc in self.errors.as_json():
            if self.profile.version.startswith("2."):
                doc["errorLevel"] = _V2_LEVEL[doc["errorLevel"]]
            wire.append(doc)
        return wire

    # ------------------------------------------------------------- error API

    def report_semantic_error(
        self, key: str, references: dict[str, str] | None = None, detail: str = ""
    ) -> None:
        if key not in self.profile.error_names:
            return  # this error concept does not exist in the active version
        level_v3, clear = PREDEFINED.get(SEMANTIC_V3[key], ("WARNING", Clear.NEW_ORDER))
        self.errors.report(
            ErrorEntry(
                error_type=self.profile.error_type(key),
                references=references or {},
                description=detail,
                level=level_v3,
                clear=clear,
                condition_key=(references or {}).get("zoneId", ""),
            )
        )
        self.touch("errors")

    # --------------------------------------------------------------- inbound

    async def _inbound_loop(self) -> None:
        while True:
            message = await self.client.messages.get()
            parsed = self._parse_topic_name(message.topic)
            if parsed is None:
                continue
            try:
                await self._dispatch(parsed, message)
            except Exception:  # noqa: S112 — one bad message must never kill the robot
                continue

    def _parse_topic_name(self, topic: str) -> str | None:
        prefix = self.topics.prefix + "/"
        return topic[len(prefix) :] if topic.startswith(prefix) else None

    async def _dispatch(self, name: str, message: Message) -> None:
        if name == EMULATOR_TOPIC:
            await self._on_emulator(message.payload)
            return
        try:
            doc = json.loads(message.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            if name in ("order", "instantActions"):
                self.report_semantic_error(
                    "validation", {"topic": name}, "message is not valid JSON"
                )
            return
        if self.hibernating and not _is_stop_hibernation(name, doc):
            return
        if name == "order":
            await self._on_order(doc)
        elif name == "instantActions":
            await self._on_instant_actions(doc)
        elif name == "zoneSet" and self.profile.has_zones:
            await self._on_zone_set(doc)
        elif name == "responses" and self.profile.has_zones:
            await self._on_responses(doc)

    # ----------------------------------------------------------------- orders

    def _situation(self) -> order_mod.Situation:
        supported = self.profile.supported_actions
        node_actions = {a for a in supported if "NODE" in factsheet_mod.action_scopes(a)}
        edge_actions = {a for a in supported if "EDGE" in factsheet_mod.action_scopes(a)}
        decision_point = None
        base_nodes = [n for n in self._nodes.values() if n["released"]]
        if base_nodes:
            last = max(base_nodes, key=lambda n: n["sequenceId"])
            decision_point = (last["nodeId"], last["sequenceId"])
        return order_mod.Situation(
            order_id=self.order_id,
            order_update_id=self.order_update_id,
            has_order=self.has_order,
            idle=self.is_idle(),
            cancelled=self.cancelled,
            waiting_for_update=bool(self.node_states or self.edge_states),
            decision_point=decision_point,
            position=(self.x, self.y) if self.localized else None,
            theta=self.theta,
            last_node_id=self.last_node_id,
            map_id=self.map_id,
            known_maps=frozenset(m["mapId"] for m in self.maps)
            if self.profile.has_maps
            else frozenset({self.map_id}),
            supported_actions=supported,
            supported_node_actions=frozenset(node_actions),
            supported_edge_actions=frozenset(edge_actions),
            accepts_orders=self.accepts_orders(),
            edges_carry_node_ids=self.profile.edges_carry_node_ids,
        )

    def accepts_orders(self) -> bool:
        allowed_modes = ("AUTOMATIC", "SEMIAUTOMATIC", "INTERVENED")
        return self._wire_operating_mode() in allowed_modes and not self.errors.fatal

    def is_idle(self) -> bool:
        settled = all(a["actionStatus"] in ("FINISHED", "FAILED") for a in self.action_states)
        return not self.node_states and not self.edge_states and settled

    async def _on_order(self, doc: dict) -> None:
        problems = validation_errors_for(self.profile.version, "order", doc)
        if problems:
            self.report_semantic_error(
                "validation",
                {"topic": "order", "orderId": str(doc.get("orderId", ""))},
                f"schema violations: {problems[:3]}",
            )
            return
        decision = order_mod.evaluate(doc, self._situation())
        if decision.verdict == "ignore":
            digest = _order_digest(doc)
            if digest != self._last_order_digest:
                self.report_semantic_error(
                    "same_order_update",
                    {
                        "orderId": doc["orderId"],
                        "orderUpdateId": str(doc["orderUpdateId"]),
                    },
                    "same orderUpdateId with different content",
                )
            return
        if decision.verdict == "reject":
            self.report_semantic_error(decision.error_key, decision.references, decision.detail)
            return
        self._accept_order(doc, decision)

    def _accept_order(self, doc: dict, decision: order_mod.Decision) -> None:
        self.errors.clear_for(Clear.NEW_ORDER)
        self._last_order_digest = _order_digest(doc)
        self.new_base_request = False
        if not decision.is_update:
            self._start_fresh_order(doc)
        else:
            self._apply_order_update(doc, decision)
        self.order_id = doc["orderId"]
        self.order_update_id = doc["orderUpdateId"]
        self.has_order = True
        self.cancelled = False
        self.touch("order accepted")

    def _start_fresh_order(self, doc: dict) -> None:
        for run in self._runs.values():
            if run.task is not None and not run.task.done():
                run.task.cancel()
        self._runs = {r.action_id: r for r in self._instant_runs()}
        self.engine.queue.clear()
        self.engine.active = [r for r in self.engine.active if r.origin == "instant"]
        self._nodes = {n["sequenceId"]: n for n in doc["nodes"]}
        self._edges = {e["sequenceId"]: e for e in doc["edges"]}
        self.action_states = []
        self.node_states = []
        self.edge_states = []
        first = doc["nodes"][0]
        for node in doc["nodes"][1:]:
            self.node_states.append(_node_state(node))
        for edge in doc["edges"]:
            self.edge_states.append(_edge_state(edge))
        for element in (*doc["nodes"], *doc["edges"]):
            for action in element.get("actions", ()):
                self._register_order_action(action, element)
        # The first node is trivially reachable: the robot stands on it.
        self.last_node_id = first["nodeId"]
        self.last_node_sequence_id = first["sequenceId"]
        self.distance_since_last_node = 0.0
        position = first.get("nodePosition")
        if isinstance(position, dict):
            self.x = float(position["x"])
            self.y = float(position["y"])
            if position.get("theta") is not None:
                self.theta = float(position["theta"])
            self.map_id = position.get("mapId", self.map_id)
        self._enqueue_element_actions(first)
        self._driver_wake.set()

    def _apply_order_update(self, doc: dict, decision: order_mod.Decision) -> None:
        stitch_seq = decision.append_from
        removed_ids: set[str] = set()
        for seq in [s for s in self._nodes if s > stitch_seq]:
            removed_ids.update(
                a.get("actionId", "") for a in self._nodes.pop(seq).get("actions", ())
            )
        for seq in [s for s in self._edges if s > stitch_seq]:
            removed_ids.update(
                a.get("actionId", "") for a in self._edges.pop(seq).get("actions", ())
            )
        self.node_states = [n for n in self.node_states if n["sequenceId"] <= stitch_seq]
        self.edge_states = [e for e in self.edge_states if e["sequenceId"] <= stitch_seq]
        self.action_states = [a for a in self.action_states if a["actionId"] not in removed_ids]
        for action_id in removed_ids:
            self._runs.pop(action_id, None)
        self.engine.drop_horizon_states(set(self._runs))

        stitch_traversed = self.last_node_sequence_id >= stitch_seq
        for node in doc["nodes"]:
            seq = node["sequenceId"]
            if seq == stitch_seq:
                existing = self._nodes.get(seq)
                known = {a.get("actionId") for a in (existing or {}).get("actions", ())}
                fresh = [a for a in node.get("actions", ()) if a.get("actionId") not in known]
                self._nodes[seq] = node
                for action in fresh:
                    run = self._register_order_action(action, node)
                    if stitch_traversed and run is not None:
                        self.engine.enqueue([run])
                continue
            self._nodes[seq] = node
            self.node_states.append(_node_state(node))
            for action in node.get("actions", ()):
                self._register_order_action(action, node)
        for edge in doc["edges"]:
            seq = edge["sequenceId"]
            if seq <= stitch_seq:
                continue
            self._edges[seq] = edge
            self.edge_states.append(_edge_state(edge))
            for action in edge.get("actions", ()):
                self._register_order_action(action, edge)
        self._driver_wake.set()

    def _register_order_action(self, action: dict, element: dict) -> ActionRun | None:
        action_id = action.get("actionId", "")
        if action_id in self._runs:
            return None
        state = {"actionId": action_id, "actionStatus": "WAITING"}
        if action.get("actionType"):
            state["actionType"] = action["actionType"]
        self.action_states.append(state)
        origin = "edge" if "edgeId" in element else "node"
        run = ActionRun(
            action=action, state=state, origin=origin, element_sequence=element["sequenceId"]
        )
        self._runs[action_id] = run
        return run

    def _instant_runs(self) -> list[ActionRun]:
        return [r for r in self._runs.values() if r.origin == "instant"]

    def _enqueue_element_actions(self, element: dict) -> None:
        runs = [
            self._runs[a["actionId"]]
            for a in element.get("actions", ())
            if a.get("actionId") in self._runs and self._runs[a["actionId"]].status == "WAITING"
        ]
        if runs:
            self.engine.enqueue(runs)
            self.touch("actions enqueued")

    # -------------------------------------------------------- instant actions

    async def _on_instant_actions(self, doc: dict) -> None:
        problems = validation_errors_for(self.profile.version, "instantActions", doc)
        if problems:
            self.report_semantic_error(
                "validation", {"topic": "instantActions"}, f"schema violations: {problems[:3]}"
            )
            return
        self.errors.clear_for(Clear.NEW_INSTANT_ACTION)
        for action in doc.get("actions", []):
            self._start_instant_action(action)

    def _start_instant_action(self, action: dict) -> None:
        action_type = action.get("actionType", "")
        action_id = action.get("actionId") or f"instant-{uuid.uuid4()}"
        state = {"actionId": action_id, "actionStatus": "WAITING", "actionType": action_type}
        self.instant_action_states.append(state)
        run = ActionRun(action=action, state=state, origin="instant")
        self._runs[action_id] = run
        supported = (
            action_type in self.profile.supported_actions
            and "INSTANT" in factsheet_mod.action_scopes(action_type)
        )
        mode = self._wire_operating_mode()
        mode_allows = mode in ("AUTOMATIC", "SEMIAUTOMATIC") or (
            mode == "INTERVENED" and action_type == "cancelOrder"
        )
        if not supported or not mode_allows:
            self.set_action_status(run, "FAILED", result="unsupported instant action")
            self.report_semantic_error(
                "invalid_instant_action",
                {"actionId": action_id, "topic": "instantActions"},
                f"unsupported instant action {action_type!r}"
                if not supported
                else f"instant actions not allowed in operating mode {mode}",
            )
            return
        self.engine.start_instant(run)
        self.touch("instant action")

    # ------------------------------------------------------ zoneSet/responses

    async def _on_zone_set(self, doc: dict) -> None:
        problems = validation_errors_for(self.profile.version, "zoneSet", doc)
        if problems:
            self.report_semantic_error(
                "validation", {"topic": "zoneSet"}, f"schema violations: {problems[:3]}"
            )
            return
        zone_set = doc["zoneSet"]
        unsupported = {zone["zoneType"] for zone in zone_set.get("zones", ())} - set(
            factsheet_mod.SUPPORTED_ZONES
        )
        if unsupported:
            self.report_semantic_error(
                "validation",
                {"topic": "zoneSet", "zoneSetId": zone_set["zoneSetId"]},
                f"unsupported zone types: {sorted(unsupported)}",
            )
            return
        if not self.zones.add(zone_set):
            self.report_semantic_error("duplicate_zone_set", {"zoneSetId": zone_set["zoneSetId"]})
            return
        self.touch("zone set stored")

    async def _on_responses(self, doc: dict) -> None:
        problems = validation_errors_for(self.profile.version, "responses", doc)
        if problems:
            return
        for response in doc.get("responses", []):
            entry = self.zones.apply_response(response)
            if entry is None:
                entry = self._apply_edge_response(response)
            if entry is not None:
                self.touch("request answered")
        self._driver_wake.set()

    def _apply_edge_response(self, response: dict) -> dict | None:
        for entry in self.edge_requests:
            if entry["requestId"] == response.get("requestId"):
                grant = response.get("grantType")
                if grant == "GRANTED":
                    entry["requestStatus"] = "GRANTED"
                elif grant == "REVOKED":
                    entry["requestStatus"] = "REVOKED"
                return entry
        return None

    # ----------------------------------------------------------- driving loop

    def _may_drive(self) -> bool:
        return (
            not self.paused
            and not self.hibernating
            and self.localized
            and self.emergency_stop == "NONE"
            and not self.field_violation
            and not self.errors.order_blocking
            and self._wire_operating_mode() in ("AUTOMATIC", "SEMIAUTOMATIC")
            and not self.engine.blocks_driving
        )

    def _next_edge(self) -> dict | None:
        edge = self._edges.get(self.last_node_sequence_id + 1)
        if edge is not None and edge.get("released"):
            return edge
        return None

    async def _driver_loop(self) -> None:
        while True:
            self._driver_wake.clear()
            edge = self._next_edge()
            if edge is None:
                self._update_new_base_request()
                self._set_driving(False)
                await self._driver_wake.wait()
                continue
            if not self._may_drive():
                self._set_driving(False)
                self.engine.changed.clear()
                self._situation_changed.clear()
                await _first_of(self.engine.changed.wait(), self._situation_changed.wait())
                continue
            await self._traverse(edge)

    async def _traverse(self, edge: dict) -> None:
        target = self._nodes[edge["sequenceId"] + 1]
        start = self._nodes.get(edge["sequenceId"] - 1)
        length = _edge_length(edge, start, target)
        base_speed = min(
            float(edge.get("maximumSpeed") or self.config.default_speed),
            self.config.max_speed,
        )
        start_xy = _node_xy(start) or (self.x, self.y)
        target_xy = _node_xy(target)
        heading = None
        if target_xy is not None:
            heading = math.atan2(target_xy[1] - start_xy[1], target_xy[0] - start_xy[0])
        self._enqueue_edge_actions(edge)
        travelled = 0.0
        self._set_driving(True)
        while travelled < length:
            if not self._may_drive():
                self._set_driving(False)
                self.engine.changed.clear()
                self._situation_changed.clear()
                await _first_of(self.engine.changed.wait(), self._situation_changed.wait())
                if self._edges.get(edge["sequenceId"]) is not edge:
                    return  # order was cancelled/cleared while stopped
                self._set_driving(True)
                continue
            speed = base_speed
            if self.profile.has_zones:
                limit = self.zones.speed_limit_at(self.x, self.y, self.map_id)
                if limit is not None:
                    speed = min(speed, limit)
            dt = min(0.25, max(0.02, length / speed / 25.0))
            step = min(speed * dt, length - travelled)
            fraction = (travelled + step) / length if length else 1.0
            next_xy = (
                (
                    start_xy[0] + (target_xy[0] - start_xy[0]) * fraction,
                    start_xy[1] + (target_xy[1] - start_xy[1]) * fraction,
                )
                if target_xy is not None
                else (self.x, self.y)
            )
            if self.profile.has_zones and not await self._zone_gate(next_xy, edge, target):
                continue  # stopped at a zone boundary; retry after wake-up
            await self.clock.sleep(dt)
            if self._edges.get(edge["sequenceId"]) is not edge:
                return  # order changed under us (cancel / clear)
            travelled += step
            self.x, self.y = next_xy
            if heading is not None:
                self.theta = heading
                self.velocity = (
                    speed * math.cos(heading),
                    speed * math.sin(heading),
                    0.0,
                )
            else:
                self.velocity = (speed, 0.0, 0.0)
            self.distance_since_last_node += step
            if self.profile.has_zones:
                self._evaluate_zone_membership()
        self._arrive(edge, target)

    async def _zone_gate(self, next_xy: tuple[float, float], edge: dict, target: dict) -> bool:
        """Enforce BLOCKED and RELEASE zones on the position we are about to
        enter. Returns False after stopping the robot at the boundary."""
        x, y = next_xy
        blocked = self.zones.blocking_zone_at(x, y, self.map_id)
        if blocked is not None:
            self.report_semantic_error(
                "node_unreachable",
                {"nodeId": target["nodeId"], "zoneId": blocked["zoneId"]},
                "path enters a BLOCKED zone",
            )
            self._set_driving(False)
            self.engine.changed.clear()
            self._situation_changed.clear()
            await _first_of(self.engine.changed.wait(), self._situation_changed.wait())
            return False
        for zone_set, zone in self.zones.release_zones_at(x, y, self.map_id):
            status = self.zones.status(zone_set.zone_set_id, zone["zoneId"])
            if status == "GRANTED":
                continue
            if status is None:
                self.zones.request_access(zone_set, zone)
                self.touch("zone request")
            self._set_driving(False)
            self._situation_changed.clear()
            await self._situation_changed.wait()
            return False
        return True

    def _evaluate_zone_membership(self) -> None:
        zones_here = self.zones.active_zones_at(self.x, self.y, self.map_id)
        entered, _exited, _ = self._zone_membership.transitions(zones_here)
        for zone in entered:
            for action in zone.get("entryActions", []) + zone.get("duringActions", []):
                self._start_zone_action(action, zone)
        blocked = next((z for _, z in zones_here if z["zoneType"] == "BLOCKED"), None)
        if blocked is not None:
            self.report_semantic_error(
                "blocked_zone", {"zoneId": blocked["zoneId"]}, "robot is inside a BLOCKED zone"
            )
        else:
            self.errors.clear_condition(self.profile.error_type("blocked_zone"))
        for zone_set, zone in self.zones.release_zones_at(self.x, self.y, self.map_id):
            entry_status = self.zones.status(zone_set.zone_set_id, zone["zoneId"])
            if entry_status in ("REVOKED", "EXPIRED"):
                behavior = zone.get("releaseLossBehavior", "STOP")
                if behavior == "STOP":
                    self.report_semantic_error(
                        "release_lost", {"zoneId": zone["zoneId"]}, "release lost inside zone"
                    )
        exited_release = [
            entry
            for entry in list(self.zones.zone_requests)
            if entry["requestStatus"] in ("GRANTED", "REVOKED", "EXPIRED")
            and not any(
                z["zoneId"] == entry["zoneId"]
                for _, z in self.zones.active_zones_at(self.x, self.y, self.map_id)
            )
        ]
        for entry in exited_release:
            self.zones.remove_request(entry["requestId"])
            self.errors.clear_condition(self.profile.error_type("release_lost"), entry["zoneId"])
        for entry in self.zones.expire_leases(self.clock.now_iso()):
            self.touch(f"lease expired for {entry['requestId']}")

    def _start_zone_action(self, action: dict, zone: dict) -> None:
        run_action = dict(action)
        run_action["actionId"] = f"zone-{zone['zoneId']}-{uuid.uuid4().hex[:8]}"
        state = {
            "actionId": run_action["actionId"],
            "actionStatus": "WAITING",
            "actionType": run_action.get("actionType", ""),
        }
        self.zone_action_states.append(state)
        run = ActionRun(action=run_action, state=state, origin="zone")
        self._runs[run_action["actionId"]] = run
        self.engine.enqueue([run])

    def _enqueue_edge_actions(self, edge: dict) -> None:
        self._enqueue_element_actions(edge)

    def _arrive(self, edge: dict, node: dict) -> None:
        self.velocity = (0.0, 0.0, 0.0)
        position = node.get("nodePosition")
        if isinstance(position, dict):
            self.x, self.y = float(position["x"]), float(position["y"])
            if position.get("theta") is not None:
                self.theta = float(position["theta"])
            self.map_id = position.get("mapId", self.map_id)
        self.last_node_id = node["nodeId"]
        self.last_node_sequence_id = node["sequenceId"]
        self.distance_since_last_node = 0.0
        self.node_states = [n for n in self.node_states if n["sequenceId"] != node["sequenceId"]]
        self.edge_states = [e for e in self.edge_states if e["sequenceId"] != edge["sequenceId"]]
        self.engine.finish_edge_actions(edge["sequenceId"])
        self._enqueue_element_actions(node)
        self._update_new_base_request()
        self.touch("node traversed")

    def _update_new_base_request(self) -> None:
        horizon_exists = any(not n.get("released") for n in self._nodes.values())
        base_exhausted = self._next_edge() is None
        value = horizon_exists and base_exhausted
        if value != self.new_base_request:
            self.new_base_request = value
            self.touch("newBaseRequest")

    def _set_driving(self, driving: bool) -> None:
        if driving != self.driving:
            self.driving = driving
            if not driving:
                self.velocity = (0.0, 0.0, 0.0)
            self._reanchor_battery()
            self.touch("driving")

    # ------------------------------------------------------- action callbacks

    def set_action_status(self, run: ActionRun, status: str, result: str | None = None) -> None:
        if run.state.get("actionStatus") == status and result is None:
            return
        run.state["actionStatus"] = status
        if result is not None:
            run.state["actionResult"] = result
        self.touch(f"action {run.action_id} -> {status}")

    async def action_progress(
        self, run: ActionRun, duration: float, *, initializing: bool = True
    ) -> None:
        """INITIALIZING -> RUNNING over ``duration`` simulated seconds,
        honouring pause for pauseable actions."""
        if initializing:
            self.set_action_status(run, "INITIALIZING")
            await self.clock.sleep(min(0.2, duration / 10))
        self.set_action_status(run, "RUNNING")
        remaining = duration
        while remaining > 0:
            if self.paused and run.pause_allowed:
                self.set_action_status(run, "PAUSED")
                self._situation_changed.clear()
                while self.paused:
                    await self._situation_changed.wait()
                    self._situation_changed.clear()
                self.set_action_status(run, "RUNNING")
            step = min(0.5, remaining)
            await self.clock.sleep(step)
            remaining -= step

    def set_paused(self, paused: bool) -> None:
        if self.paused != paused:
            self.paused = paused
            self.touch("paused")

    def set_charging(self, charging: bool) -> None:
        if self.charging != charging:
            self._reanchor_battery()
            self.charging = charging
            self.touch("charging")

    def set_load(self, action_params: dict) -> None:
        load = {
            "loadId": str(action_params.get("loadId", f"load-{uuid.uuid4().hex[:8]}")),
            "loadType": str(action_params.get("loadType", "EPAL")),
            "loadPosition": str(action_params.get("lhd", "deck")),
        }
        self.loads.append(load)
        self.touch("load")

    def clear_load(self) -> None:
        self.loads.clear()
        self.touch("load")

    def clear_settled_instant_actions(self, keep: str = "") -> None:
        self.instant_action_states = [
            a
            for a in self.instant_action_states
            if a["actionStatus"] not in ("FINISHED", "FAILED") or a["actionId"] == keep
        ]
        self.touch("instant actions cleared")

    def clear_settled_zone_actions(self) -> None:
        self.zone_action_states = [
            a for a in self.zone_action_states if a["actionStatus"] not in ("FINISHED", "FAILED")
        ]
        self.touch("zone actions cleared")

    def release_wait_for_trigger(self) -> bool:
        released = False
        for run in self._runs.values():
            if run.action_type == "waitForTrigger" and run.status == "RUNNING":
                run.trigger_event.set()
                released = True
        return released

    def map_known(self, map_id: str) -> bool:
        return any(m["mapId"] == map_id for m in self.maps)

    def map_on_robot(self, map_id: str, map_version: str) -> bool:
        return any(m["mapId"] == map_id and m["mapVersion"] == map_version for m in self.maps)

    def add_map(self, map_id: str, map_version: str) -> None:
        self.maps.append({"mapId": map_id, "mapVersion": map_version, "mapStatus": "DISABLED"})
        self.touch("maps")

    def enable_map(self, map_id: str, map_version: str) -> bool:
        target = None
        for entry in self.maps:
            if entry["mapId"] == map_id and entry["mapVersion"] == map_version:
                target = entry
        if target is None:
            return False
        for entry in self.maps:
            if entry["mapId"] == map_id:
                entry["mapStatus"] = "DISABLED"
        target["mapStatus"] = "ENABLED"
        self.touch("maps")
        return True

    def delete_map(self, map_id: str, map_version: str) -> bool:
        for entry in list(self.maps):
            if entry["mapId"] == map_id and entry["mapVersion"] == map_version:
                if entry["mapStatus"] == "ENABLED":
                    return False  # currently in use
                self.maps.remove(entry)
                self.touch("maps")
                return True
        return False

    def teleport(
        self,
        *,
        x: float | None = None,
        y: float | None = None,
        theta: float | None = None,
        map_id: str | None = None,
        last_node_id: str | None = None,
    ) -> None:
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if theta is not None:
            self.theta = theta
        if map_id is not None:
            self.map_id = map_id
        if last_node_id is not None:
            self.last_node_id = last_node_id
            self.last_node_sequence_id = 0
        self.localized = True
        self.errors.clear_condition(self.profile.error_type("localization"))
        if self.profile.has_zones:
            self._evaluate_zone_membership()
        self.touch("teleport")

    # ------------------------------------------------- order-level operations

    async def handle_cancel_order(self, run: ActionRun) -> None:
        from .actions import ActionFailure

        requested = params(run.action).get("orderId")
        if (
            self.is_idle()
            or self.cancelled
            or (requested is not None and str(requested) != self.order_id)
        ):
            self.report_semantic_error(
                "no_order_to_cancel", {"actionId": run.action_id}, "no matching active order"
            )
            raise ActionFailure("no active order to cancel")
        self.set_action_status(run, "RUNNING")
        self.cancelled = True
        outstanding = self.engine.cancel_order_actions()
        self._clear_order_execution()
        for pending in outstanding:
            await pending.finished_event.wait()
        self.set_action_status(run, "FINISHED")
        self.touch("order cancelled")

    def _clear_order_execution(self) -> None:
        """6.6.7: node/edge states empty, ids kept, requests removed."""
        self.node_states = []
        self.edge_states = []
        self._edges = {}
        self._nodes = {}
        self.zones.clear_requests()
        self.edge_requests = []
        self.new_base_request = False
        self.velocity = (0.0, 0.0, 0.0)
        self._driver_wake.set()
        self.touch("order cleared")

    async def handle_start_hibernation(self, run: ActionRun, wake_up_time: Any) -> None:
        self.set_action_status(run, "RUNNING")
        if not self.is_idle():
            self.cancelled = True
            outstanding = self.engine.cancel_order_actions()
            self._clear_order_execution()
            for pending in outstanding:
                await pending.finished_event.wait()
        self.set_action_status(run, "FINISHED")
        await self.publish_state(reason="hibernation")
        self.hibernating = True
        self.connection_state = "HIBERNATING"
        await self._publish("connection", {"connectionState": "HIBERNATING"}, qos=1, retain=True)
        if wake_up_time:
            self._wake_task = asyncio.create_task(self._auto_wake(str(wake_up_time)))

    async def _auto_wake(self, wake_up_time: str) -> None:
        while self.clock.now_iso() < wake_up_time:
            await self.clock.sleep(1.0)
        if self.hibernating:
            self.hibernating = False
            self.connection_state = "ONLINE"
            await self._publish("connection", {"connectionState": "ONLINE"}, qos=1, retain=True)
            self.touch("woke from hibernation")

    async def handle_stop_hibernation(self, run: ActionRun) -> None:
        self.set_action_status(run, "RUNNING")
        if self._wake_task is not None:
            self._wake_task.cancel()
            self._wake_task = None
        self.hibernating = False
        self.connection_state = "ONLINE"
        await self._publish("connection", {"connectionState": "ONLINE"}, qos=1, retain=True)
        self.set_action_status(run, "FINISHED")
        self.touch("hibernation ended")

    async def handle_shutdown(self, run: ActionRun) -> None:
        from .actions import ActionFailure

        if not self.is_idle():
            raise ActionFailure("shutdown requires an idle robot")
        self.set_action_status(run, "RUNNING")
        self.set_action_status(run, "FINISHED")
        await self.publish_state(reason="shutdown")
        asyncio.get_running_loop().call_soon(lambda: asyncio.ensure_future(self.stop()))

    # ------------------------------------------------------- fault injection

    async def _on_emulator(self, payload: bytes) -> None:
        try:
            doc = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        if not isinstance(doc, dict):
            return
        self.inject(**{_snake(k): v for k, v in doc.items()})
        if doc.get("disconnect") == "drop":
            await self.drop_connection()

    def inject(
        self,
        *,
        emergency_stop: str | None = None,
        field_violation: bool | None = None,
        localized: bool | None = None,
        battery: dict | None = None,
        teleport: dict | None = None,
        operating_mode: str | None = None,
        action_failure: dict | None = None,
        time_scale: float | None = None,
        trigger: bool | None = None,
        request_corridor: dict | None = None,
        **_ignored: Any,
    ) -> None:
        """Python fault-injection API (also reachable via the _emulator topic)."""
        if emergency_stop is not None and emergency_stop in ("MANUAL", "REMOTE", "NONE"):
            self.emergency_stop = emergency_stop
            self.touch("emergencyStop")
        if field_violation is not None:
            self.field_violation = bool(field_violation)
            self.touch("fieldViolation")
        if localized is not None:
            self.localized = bool(localized)
            if not self.localized:
                self.report_semantic_error("localization", {}, "localization lost")
            else:
                self.errors.clear_condition(self.profile.error_type("localization"))
            self.touch("localization")
        if battery is not None:
            if "level" in battery:
                self._reanchor_battery(float(battery["level"]))
            if "charging" in battery:
                self.set_charging(bool(battery["charging"]))
            self.touch("battery")
        if teleport is not None:
            self.teleport(
                x=_maybe_float(teleport.get("x")),
                y=_maybe_float(teleport.get("y")),
                theta=_maybe_float(teleport.get("theta")),
                map_id=teleport.get("mapId"),
                last_node_id=teleport.get("lastNodeId"),
            )
        if operating_mode is not None:
            self._switch_operating_mode(operating_mode)
        if action_failure is not None:
            key = action_failure.get("actionId") or action_failure.get("actionType")
            if key:
                self.forced_action_failures[str(key)] = str(action_failure.get("mode", "FAILED"))
        if time_scale is not None:
            self.clock.set_scale(float(time_scale))
        if trigger:
            self.release_wait_for_trigger()

        if request_corridor is not None:
            entry = {
                "requestId": f"edge-req-{uuid.uuid4().hex[:8]}",
                "requestType": "CORRIDOR",
                "edgeId": str(request_corridor.get("edgeId", "")),
                "sequenceId": int(request_corridor.get("sequenceId", 0)),
                "requestStatus": "REQUESTED",
            }
            self.edge_requests.append(entry)
            self.touch("edge request")

    def _switch_operating_mode(self, mode: str) -> None:
        mode = "TEACH_IN" if mode in ("TEACHIN", "TEACH_IN") else mode
        known = (
            "AUTOMATIC",
            "SEMIAUTOMATIC",
            "INTERVENED",
            "MANUAL",
            "SERVICE",
            "TEACH_IN",
            "STARTUP",
        )
        if mode not in known:
            return
        if mode in ("INTERVENED", "STARTUP") and self.profile.version.startswith("2."):
            return  # these modes do not exist in 2.x
        self.operating_mode = mode
        if mode == "INTERVENED":
            # Table 11: INTERVENED keeps the order but clears zone requests.
            self.zones.clear_requests()
        if mode in ("MANUAL", "SERVICE", "TEACH_IN", "STARTUP"):
            # 6.6.7: entering these modes clears the current order.
            for run in list(self._runs.values()):
                if run.origin != "instant" and not run.settled:
                    if run.task is not None and not run.task.done():
                        run.task.cancel()
                    else:
                        self.set_action_status(run, "FAILED", result="order cleared")
                        run.finished_event.set()
            self.engine.cancel_order_actions()
            self._clear_order_execution()
            self.last_node_id = ""
        self.touch("operatingMode")


# ---------------------------------------------------------------- module bits


def validation_errors_for(version: str, message_type: str, message: object) -> list[str]:
    return validation_errors(message_type, message, tag=version)


def _order_digest(doc: dict) -> str:
    content = {k: v for k, v in doc.items() if k not in ("headerId", "timestamp")}
    return json.dumps(content, sort_keys=True)


def _node_state(node: dict) -> dict:
    state = {
        "nodeId": node["nodeId"],
        "sequenceId": node["sequenceId"],
        "released": bool(node["released"]),
    }
    if isinstance(node.get("nodePosition"), dict):
        state["nodePosition"] = node["nodePosition"]
    return state


def _edge_state(edge: dict) -> dict:
    state = {
        "edgeId": edge["edgeId"],
        "sequenceId": edge["sequenceId"],
        "released": bool(edge["released"]),
    }
    if isinstance(edge.get("trajectory"), dict):
        state["trajectory"] = edge["trajectory"]
    return state


def _node_xy(node: dict | None) -> tuple[float, float] | None:
    if node is None:
        return None
    position = node.get("nodePosition")
    if isinstance(position, dict):
        return float(position["x"]), float(position["y"])
    return None


def _edge_length(edge: dict, start: dict | None, target: dict) -> float:
    if edge.get("length") is not None:
        return max(0.01, float(edge["length"]))
    trajectory = edge.get("trajectory")
    if isinstance(trajectory, dict):
        points = trajectory.get("controlPoints", [])
        if len(points) >= 2:
            total = 0.0
            for a, b in itertools.pairwise(points):
                total += math.dist((float(a["x"]), float(a["y"])), (float(b["x"]), float(b["y"])))
            return max(0.01, total)
    start_xy, target_xy = _node_xy(start), _node_xy(target)
    if start_xy is not None and target_xy is not None:
        return max(0.01, math.dist(start_xy, target_xy))
    return 2.0


def _maybe_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _snake(camel: str) -> str:
    out = []
    for ch in camel:
        if ch.isupper():
            out.append("_")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out)


def _is_stop_hibernation(name: str, doc: dict) -> bool:
    return name == "instantActions" and any(
        a.get("actionType") == "stopHibernation" for a in doc.get("actions", [])
    )


async def _first_of(*aws) -> None:
    tasks = [asyncio.ensure_future(a) for a in aws]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for task in tasks:
            task.cancel()
