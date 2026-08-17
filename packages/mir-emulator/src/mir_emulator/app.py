"""Spec-driven Starlette application factory.

Every operation in the loaded MiR spec becomes a route under its base path
(/api/v2.0.0). Behavior overlays (behaviors.py) handle the interesting
stateful endpoints; everything else gets generic, schema-faithful CRUD.

Sessions: every request may carry ``X-MiR-Session: <id>`` to get its own
virtual robot — an isolated StateStore (own mission queue, registers, status
overrides) — so many users can run simulations against one emulator without
trampling each other. No header means the shared default robot. Session
stores are LRU-capped so a public deployment can't be memory-exhausted by
invented session ids.
"""

from __future__ import annotations

import asyncio
import json
import math
import re
import threading
from collections import OrderedDict
from typing import Any

from jsonschema import Draft4Validator
from jsonschema.exceptions import SchemaError
from starlette.applications import Starlette
from starlette.datastructures import MutableHeaders
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from mir_emulator import auth, registry
from mir_emulator.behaviors import (
    FAULTS,
    MISSION_DURATION_S,
    OVERRIDES,
    RequestCtx,
    active_faults,
    battery_doc,
    clock_doc,
    faults_doc,
    get_status,
    reset_battery,
    reset_time_scale,
    set_battery,
    set_faults,
    set_time_scale,
)
from mir_emulator.examples import example_from_schema, overlay_compatible
from mir_emulator.openapi3 import to_openapi3
from mir_emulator.record import (
    clear_recording,
    record_step,
    scenario_doc,
    set_recording,
)
from mir_emulator.spec import Operation, Spec, load_spec
from mir_emulator.state import StateStore

MAX_BODY_BYTES = 2 * 1024 * 1024
SESSION_HEADER = "x-mir-session"
# Emulator-only network shaping: X-MiR-Latency: <milliseconds> delays the
# response (robots live on factory Wi-Fi; timeout paths deserve tests).
# Capped so a hostile header can't hold a worker hostage.
LATENCY_HEADER = "x-mir-latency"
MAX_LATENCY_MS = 10_000.0
# Emulator-only mission shaping: X-MiR-Mission-Duration: <seconds> on
# POST /mission_queue freezes that duration onto the new entry, so one
# robot can mix long hauls and short hops (real routes are not uniform).
DURATION_HEADER = "x-mir-mission-duration"
MIN_MISSION_DURATION_S = 0.1
MAX_MISSION_DURATION_S = 3600.0
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
MAX_SESSIONS = 256
# Body validation reports every violation in one 400 (a client shouldn't
# rediscover required fields one round trip at a time), bounded so a
# pathological body can't inflate the response.
MAX_VALIDATION_ERRORS = 16


def _error_body(status: int, human: str) -> dict:
    return {"error_code": str(status), "error_human": human}


class _DroppedConnection(Response):
    """Sever the connection mid-response: declare a body length, send one
    byte, then abandon the exchange. A real HTTP server (uvicorn) aborts the
    connection, so the client observes the transport failure a rebooting
    robot produces — never an HTTP status. In-process ASGI test clients
    surface the abandonment as a server-side error instead."""

    async def __call__(self, scope, receive, send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json"), (b"content-length", b"1024")],
            }
        )
        await send({"type": "http.response.body", "body": b"{", "more_body": True})
        # Returning without completing the declared body makes the server
        # tear the connection down.


def _respond(status: int, body: Any, media_type: str = "application/json") -> Response:
    if status == 204 or body is None:
        return Response(status_code=status)
    if media_type != "application/json":
        return Response(body, status_code=status, media_type=media_type)
    return JSONResponse(body, status_code=status)


def _starlette_path(op: Operation) -> str:
    path = op.path
    for name, ptype in op.path_param_types().items():
        if ptype == "integer":
            path = path.replace("{" + name + "}", "{" + name + ":int}")
    return path


def _is_item_op(op: Operation) -> bool:
    return op.path.rsplit("/", 1)[-1].startswith("{")


def parse_latency_ms(header_value: str | None, default: float) -> float | None:
    """Effective delay in ms; None signals an invalid header (a 400)."""
    if header_value is None:
        return min(max(default, 0.0), MAX_LATENCY_MS)
    try:
        requested = float(header_value)
    except ValueError:
        return None
    if requested < 0 or math.isnan(requested):
        return None
    return min(requested, MAX_LATENCY_MS)


def _draft4_nullable(schema: Any) -> Any:
    """OpenAPI 3.0 marks optional-null with ``nullable: true``, which Draft-4
    validation ignores and then rejects the null. Fold it into a type union."""
    if isinstance(schema, list):
        return [_draft4_nullable(s) for s in schema]
    if not isinstance(schema, dict):
        return schema
    out = {k: _draft4_nullable(v) for k, v in schema.items()}
    if out.pop("nullable", False) and isinstance(out.get("type"), str):
        out["type"] = [out["type"], "null"]
    return out


def _storage_key(op: Operation, path_params: dict) -> tuple[str, str | None]:
    """(collection key, item id). Context params are baked into the key so
    e.g. /mission_queue/1/actions and /mission_queue/2/actions don't share."""
    if _is_item_op(op):
        template, last = op.path.rsplit("/", 1)
        id_name = last.strip("{}").split(":")[0]
        item_id = str(path_params.get(id_name, ""))
    else:
        template, id_name, item_id = op.path, None, None
    context = "&".join(f"{k}={v}" for k, v in sorted(path_params.items()) if k != id_name)
    return (f"{template}?{context}" if context else template), item_id


class Emulator:
    def __init__(
        self,
        spec: Spec,
        *,
        enforce_auth: bool = True,
        username: str = auth.DEFAULT_USERNAME,
        password: str = auth.DEFAULT_PASSWORD,
        seed: bool = True,
        mission_duration: float = MISSION_DURATION_S,
        latency_ms: float = 0.0,
    ) -> None:
        self.spec = spec
        self.state = StateStore()  # the shared default robot (no session header)
        self.enforce_auth = enforce_auth
        self.username = username
        self.password = password
        self.seed = seed
        self.mission_duration = mission_duration
        self.latency_ms = latency_ms
        self._sessions: OrderedDict[str, StateStore] = OrderedDict()
        self._sessions_lock = threading.Lock()

    def state_for(self, session_id: str) -> StateStore:
        """The default store, or an isolated per-session virtual robot."""
        if not session_id:
            return self.state
        with self._sessions_lock:
            store = self._sessions.get(session_id)
            if store is None:
                store = StateStore()
                self._sessions[session_id] = store
            self._sessions.move_to_end(session_id)
            while len(self._sessions) > MAX_SESSIONS:
                self._sessions.popitem(last=False)
            return store

    def _example(self, schema: dict | None) -> Any:
        return example_from_schema(self.spec.deref(schema))

    def _item_schema_for(self, collection_path: str) -> dict | None:
        """Schema of a single element for a collection path.

        MiR spec files frequently declare list endpoints with the element's
        object schema instead of an array — real robots return arrays. Seed
        elements from the declared schema so both shapes stay consistent.
        """
        get_op = self.spec.operations.get(("GET", collection_path))
        if get_op and get_op.success_schema:
            deref = self.spec.deref(get_op.success_schema)
            if deref.get("type") == "array":
                return deref.get("items")
            if deref.get("type") == "object" or "properties" in deref:
                return deref
        for (method, path), op in self.spec.operations.items():
            if method == "GET" and path.startswith(collection_path + "/{") and _is_item_op(op):
                return op.success_schema
        return None

    def _assign_ids(self, item: dict, item_id: str | int) -> None:
        if "guid" in item:
            item["guid"] = str(item_id)
        elif "id" in item and isinstance(item.get("id"), int):
            item["id"] = int(item_id)

    def _seed_collection(self, state: StateStore, key: str, collection_path: str) -> None:
        if not self.seed:
            state.seed_once(key, [])
            return
        schema = self._item_schema_for(collection_path)
        item = self._example(schema)
        if not isinstance(item, dict):
            state.seed_once(key, [])
            return
        if "id" in item and isinstance(item["id"], int):
            item_id: str | int = state.next_int_id()
        else:
            item_id = state.next_guid()
        self._assign_ids(item, item_id)
        state.seed_once(key, [(str(item_id), item)])

    def _authorized(self, request: Request) -> bool:
        """MiR robot Basic auth; subclasses swap in their own scheme."""
        if not self.enforce_auth:
            return True
        return auth.is_authorized(
            request.headers.get("authorization"), self.username, self.password
        )

    def _override_for(self, op: Operation):
        """Behavior overlay for *op*, or None for the generic engine."""
        return OVERRIDES.get((op.method, op.path))

    def _validate_body(self, op: Operation, body: Any) -> str | None:
        if body is None or not op.body_schema:
            return None
        schema = _draft4_nullable(self.spec.deref(op.body_schema))
        try:
            errors = sorted(
                Draft4Validator(schema).iter_errors(body),
                key=lambda err: ([str(p) for p in err.absolute_path], err.message),
            )
        except SchemaError:
            return None  # emulator bug in the spec, not the client's fault
        if not errors:
            return None
        # err.message can embed user input; keep it JSON-encoded and
        # never log it (log injection surface).
        messages = [err.message[:200] for err in errors[:MAX_VALIDATION_ERRORS]]
        if len(errors) > MAX_VALIDATION_ERRORS:
            messages.append(f"and {len(errors) - MAX_VALIDATION_ERRORS} more")
        return "Argument error: " + "; ".join(messages)

    def handler_for(self, op: Operation):
        async def handler(request: Request) -> Response:
            return await self.handle(request, op)

        return handler

    async def handle(self, request: Request, op: Operation) -> Response:
        if not self._authorized(request):
            return _respond(401, _error_body(401, "Not authorized"))

        delay_ms = parse_latency_ms(request.headers.get(LATENCY_HEADER), self.latency_ms)
        if delay_ms is None:
            return _respond(400, _error_body(400, "Invalid X-MiR-Latency: milliseconds >= 0"))
        if delay_ms:
            await asyncio.sleep(delay_ms / 1000.0)

        session_id = request.headers.get(SESSION_HEADER, "")
        if session_id and not SESSION_ID_RE.match(session_id):
            return _respond(
                400,
                _error_body(400, "Invalid X-MiR-Session: 1-64 chars from [A-Za-z0-9._-]"),
            )

        # A connection-dropping fault kills API traffic before any handling —
        # a rebooting robot doesn't validate your request first. /_emulator/*
        # surfaces bypass this (they have their own endpoints), so the fault
        # stays clearable.
        drop_state = self.state_for(session_id)
        if any(FAULTS[n].get("drops_connections") for n in active_faults(drop_state)):
            return _DroppedConnection()

        duration_override: float | None = None
        raw_duration = request.headers.get(DURATION_HEADER)
        if raw_duration is not None:
            try:
                duration_override = float(raw_duration)
            except ValueError:
                duration_override = math.nan
            if not (MIN_MISSION_DURATION_S <= duration_override <= MAX_MISSION_DURATION_S):
                return _respond(
                    400,
                    _error_body(
                        400,
                        "Invalid X-MiR-Mission-Duration: seconds in "
                        f"[{MIN_MISSION_DURATION_S}, {MAX_MISSION_DURATION_S}]",
                    ),
                )

        body: Any = None
        if op.method in ("POST", "PUT", "PATCH"):
            raw = await request.body()
            if len(raw) > MAX_BODY_BYTES:
                return _respond(400, _error_body(400, "Payload too large"))
            if raw:
                try:
                    body = json.loads(raw)
                except ValueError:
                    return _respond(400, _error_body(400, "Invalid JSON"))
            if op.body_required and body is None:
                return _respond(400, _error_body(400, "Missing request body"))
            error = self._validate_body(op, body)
            if error:
                return _respond(400, _error_body(400, error))

        state = self.state_for(session_id)
        ctx = RequestCtx(
            spec=self.spec,
            state=state,
            op=op,
            path_params=dict(request.path_params),
            query=dict(request.query_params),
            body=body,
            mission_duration=self.mission_duration,
            seed_collection=lambda key, path: self._seed_collection(state, key, path),
            session_id=session_id,
            duration_override=duration_override,
        )

        override = self._override_for(op)
        result = await override(ctx) if override else self._generic(ctx)
        status, payload, *rest = result
        media_type = rest[0] if rest else "application/json"
        record_step(
            state,
            method=op.method,
            path=request.scope.get("path", op.path),
            query=request.scope.get("query_string", b"").decode("latin-1"),
            body=body,
            status=status,
            payload=payload,
            media_type=media_type,
        )
        return _respond(status, payload, media_type)

    def _generic(self, ctx: RequestCtx) -> tuple[int, Any]:
        op = ctx.op
        key, item_id = _storage_key(op, ctx.path_params)
        is_item = item_id is not None
        collection_path = op.path.rsplit("/", 1)[0] if is_item else op.path
        has_item_sibling = any(
            path.startswith(op.path + "/{") and _is_item_op(other)
            for (_method, path), other in self.spec.operations.items()
        )

        success_schema = self.spec.deref(op.success_schema)
        is_array_response = success_schema.get("type") == "array"

        if op.method == "GET" and not is_item and (is_array_response or has_item_sibling):
            self._seed_collection(ctx.state, key, collection_path)
            # underscore keys are emulator-internal (e.g. the verbatim client
            # body stashed at create time) — never part of the API surface
            return op.success_status, [
                {k: v for k, v in element.items() if not k.startswith("_")}
                for element in ctx.state.collection(key).values()
            ]

        if op.method == "GET" and is_item:
            self._seed_collection(ctx.state, key, collection_path)
            stored = ctx.state.get(key, item_id or "")
            if stored is None:
                return 404, _error_body(404, "Not found")
            full = self._example(op.success_schema)
            if isinstance(full, dict) and full:
                # Stored elements are list-shaped; the item schema may type
                # shared fields differently. Only merge compatible values.
                overlay_compatible(full, stored)
                if "guid" in stored:
                    full.setdefault("guid", stored["guid"])
                return op.success_status, full
            return op.success_status, {k: v for k, v in stored.items() if not k.startswith("_")}

        if op.method == "GET":
            # Singleton document (e.g. /system/info).
            doc = self._example(op.success_schema)
            if isinstance(doc, dict):
                overlay = ctx.state.singleton(op.path, {})
                doc.update({k: v for k, v in overlay.items() if k in doc})
            return op.success_status, doc

        if op.method == "POST" and (is_array_response or has_item_sibling or not is_item):
            item = self._example(op.success_schema)
            if not isinstance(item, dict):
                return op.success_status, item
            if isinstance(ctx.body, dict):
                # Echo body fields only where they fit the response schema —
                # MiR's files sometimes type a field differently in the body
                # and the response (e.g. parameters: array in, string out).
                # A schema that declares properties (even the empty document
                # POST /factory_reset answers with) caps the reply at exactly
                # those; only a shapeless schema passes the body through.
                if item:
                    overlay_compatible(item, ctx.body)
                elif not isinstance(success_schema.get("properties"), dict):
                    item.update(ctx.body)
            if "id" in item and isinstance(item.get("id"), int):
                new_id: str | int = ctx.state.next_int_id()
            else:
                new_id = ctx.state.next_guid()
            self._assign_ids(item, new_id)
            # Store a list-shaped element so GET-collection responses keep
            # validating even when the POST response schema types fields
            # differently (a real inconsistency in MiR's files).
            element_schema = self._item_schema_for(collection_path)
            element = self._example(element_schema) if element_schema else None
            if isinstance(element, dict) and element:
                overlay_compatible(element, item)
                self._assign_ids(element, new_id)
                stored = element
            else:
                stored = dict(item)
            if isinstance(ctx.body, dict):
                # Keep the client's body verbatim: response/list schemas may
                # type fields differently (parameters: array in, string out),
                # but behaviors (e.g. waypoint paths from move actions) need
                # what was actually sent. Never emitted — see the GET paths.
                stored["_request"] = dict(ctx.body)
            ctx.state.insert(key, str(item.get("guid", new_id)), stored)
            return op.success_status, item

        if op.method in ("PUT", "PATCH") and is_item:
            self._seed_collection(ctx.state, key, collection_path)
            existing = ctx.state.get(key, item_id or "")
            if existing is None:
                return 404, _error_body(404, "Not found")
            patch = ctx.body if isinstance(ctx.body, dict) else {}
            updated = overlay_compatible(dict(existing), patch)
            # The verbatim-body stash follows updates too: a PUT that changes
            # a field the response schema types differently (parameters:
            # array in, string out) must still reach behaviors that read it.
            previous_request = existing.get("_request")
            if patch:
                updated["_request"] = {
                    **(previous_request if isinstance(previous_request, dict) else {}),
                    **patch,
                }
            ctx.state.insert(key, item_id or "", updated)
            full = self._example(op.success_schema)
            if isinstance(full, dict) and full:
                overlay_compatible(full, updated)
                return op.success_status, full
            return op.success_status, {k: v for k, v in updated.items() if not k.startswith("_")}

        if op.method in ("PUT", "PATCH"):
            # Singleton update (e.g. PUT /wifi/enabled).
            doc = self._example(op.success_schema)
            if isinstance(doc, dict) and isinstance(ctx.body, dict):
                ctx.state.merge_singleton(op.path, {k: v for k, v in ctx.body.items() if k in doc})
                doc.update(ctx.state.singleton(op.path, {}))
            return op.success_status, doc

        if op.method == "DELETE" and is_item:
            self._seed_collection(ctx.state, key, collection_path)
            if not ctx.state.delete(key, item_id or ""):
                return 404, _error_body(404, "Not found")
            return op.success_status, None if op.success_status == 204 else {}

        if op.method == "DELETE":
            ctx.state.clear(key)
            return op.success_status, None if op.success_status == 204 else {}

        return op.success_status, self._example(op.success_schema)


class _SecurityHeadersMiddleware:
    """nosniff/no-store/deny-frame on every response — the emulator often runs
    on shared CI hosts and dev laptops; don't let responses be cached or
    content-sniffed into something they aren't."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.setdefault("X-Content-Type-Options", "nosniff")
                headers.setdefault("Cache-Control", "no-store")
                headers.setdefault("X-Frame-Options", "DENY")
            await send(message)

        await self.app(scope, receive, send_with_headers)


def create_app(
    mir_version: str | None = None,
    *,
    enforce_auth: bool = True,
    username: str = auth.DEFAULT_USERNAME,
    password: str = auth.DEFAULT_PASSWORD,
    seed: bool = True,
    cors: bool = False,
    mission_duration: float = MISSION_DURATION_S,
    latency_ms: float = 0.0,
) -> Starlette:
    version, path = registry.spec_path(mir_version)
    spec = load_spec(path, version)
    emulator = Emulator(
        spec,
        enforce_auth=enforce_auth,
        username=username,
        password=password,
        seed=seed,
        mission_duration=mission_duration,
        latency_ms=latency_ms,
    )

    routes = [
        Route(
            spec.base_path + _starlette_path(op),
            emulator.handler_for(op),
            methods=[op.method],
        )
        for op in spec.operations.values()
    ]

    # Serve the API definition itself, both flavors, so SDK generators and
    # contract-testing tools can point straight at the emulator.
    raw_doc = spec.document
    openapi3_doc = to_openapi3(raw_doc) if raw_doc.get("swagger") == "2.0" else raw_doc

    async def swagger_json(_request: Request) -> JSONResponse:
        return JSONResponse(raw_doc)

    async def openapi_json(_request: Request) -> JSONResponse:
        return JSONResponse(openapi3_doc)

    entry = registry.tracked_entry(version)

    async def index(_request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "name": "mir-emulator",
                "kind": "robot",
                "emulated_mir_version": version,
                "api_title": spec.title,
                "base_path": spec.base_path,
                "operations": len(spec.operations),
                "auth": "Basic BASE64(user:SHA-256(password))" if enforce_auth else "disabled",
                "sessions": (
                    "Send X-MiR-Session: <1-64 chars of A-Za-z0-9._-> for an isolated "
                    "virtual robot; omit it for the shared default robot"
                ),
                "specs": {"swagger2": "/swagger.json", "openapi3": "/openapi.json"},
                "latency": (
                    "Send X-MiR-Latency: <ms> (cap 10000) to delay any response; "
                    "or start with --latency-ms for a baseline"
                ),
                "mission_duration": (
                    "Send X-MiR-Mission-Duration: <seconds 0.1-3600> on "
                    "POST /mission_queue to give that entry its own duration "
                    "(default: --mission-duration)"
                ),
                "faults": (
                    "GET/PUT/DELETE /_emulator/faults — emulator-only fault injection "
                    f"({', '.join(sorted(FAULTS))})"
                ),
                "battery": (
                    "GET/PUT/DELETE /_emulator/battery — emulator-only battery control "
                    "(set percentage, run a charging curve via charging/charge_rate/target; "
                    "DELETE restores the stock drain model)"
                ),
                "clock": (
                    "GET/PUT/DELETE /_emulator/clock — emulator-only time scaling "
                    '(PUT {"scale": N} runs simulated time Nx wall speed with realistic '
                    "durations and timestamps, process-wide; DELETE restores 1.0)"
                ),
                "source": {
                    "primary_source": registry.primary_source(),
                    "provenance": entry["provenance"],
                    "source_url": entry.get("source_url"),
                    "source_sha256": entry.get("source_sha256"),
                    "spec_sha256": entry["sha256"],
                    "official": entry["official"],
                    "pinned": entry.get("pinned", False),
                },
            }
        )

    async def faults_endpoint(request: Request) -> Response:
        """Emulator-only fault injection (/_emulator/faults) — not part of the
        MiR API surface, hence the reserved prefix. Same auth as the API."""
        if not emulator._authorized(request):
            return _respond(401, _error_body(401, "Not authorized"))
        session_id = request.headers.get(SESSION_HEADER, "")
        if session_id and not SESSION_ID_RE.match(session_id):
            return _respond(
                400, _error_body(400, "Invalid X-MiR-Session: 1-64 chars from [A-Za-z0-9._-]")
            )
        state = emulator.state_for(session_id)
        if request.method == "DELETE":
            set_faults(state, [], emulator.mission_duration)
        elif request.method == "PUT":
            raw = await request.body()
            if len(raw) > MAX_BODY_BYTES:
                return _respond(400, _error_body(400, "Payload too large"))
            try:
                body = json.loads(raw) if raw else {}
            except ValueError:
                return _respond(400, _error_body(400, "Invalid JSON"))
            names = body.get("faults") if isinstance(body, dict) else None
            if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
                return _respond(
                    400, _error_body(400, 'Body must be {"faults": ["emergency_stop", ...]}')
                )
            unknown = sorted(set(names) - set(FAULTS))
            if unknown:
                return _respond(
                    400,
                    _error_body(400, f"Unknown faults; available: {sorted(FAULTS)}"),
                )
            set_faults(state, names, emulator.mission_duration)
        return _respond(200, faults_doc(state))

    async def battery_endpoint(request: Request) -> Response:
        """Emulator-only battery control (/_emulator/battery): set the level,
        run a charging curve toward a target, or reset to the stock drain
        model. Same auth and session semantics as the rest of the surface."""
        if not emulator._authorized(request):
            return _respond(401, _error_body(401, "Not authorized"))
        session_id = request.headers.get(SESSION_HEADER, "")
        if session_id and not SESSION_ID_RE.match(session_id):
            return _respond(
                400, _error_body(400, "Invalid X-MiR-Session: 1-64 chars from [A-Za-z0-9._-]")
            )
        state = emulator.state_for(session_id)
        if request.method == "DELETE":
            reset_battery(state)
        elif request.method == "PUT":
            raw = await request.body()
            if len(raw) > MAX_BODY_BYTES:
                return _respond(400, _error_body(400, "Payload too large"))
            try:
                body = json.loads(raw) if raw else {}
            except ValueError:
                return _respond(400, _error_body(400, "Invalid JSON"))
            error = set_battery(state, body, emulator.mission_duration)
            if error is not None:
                return _respond(400, _error_body(400, error))
        return _respond(200, battery_doc(state, emulator.mission_duration))

    async def clock_endpoint(request: Request) -> Response:
        """Emulator-only time scaling (/_emulator/clock): simulated time runs
        Nx wall speed while mission windows, battery curves and timestamps
        keep their realistic simulated lengths. Process-wide — one clock for
        every session — so no X-MiR-Session handling here."""
        if not emulator._authorized(request):
            return _respond(401, _error_body(401, "Not authorized"))
        if request.method == "DELETE":
            reset_time_scale()
        elif request.method == "PUT":
            raw = await request.body()
            if len(raw) > MAX_BODY_BYTES:
                return _respond(400, _error_body(400, "Payload too large"))
            try:
                body = json.loads(raw) if raw else {}
            except ValueError:
                return _respond(400, _error_body(400, "Invalid JSON"))
            error = set_time_scale(body)
            if error is not None:
                return _respond(400, _error_body(400, error))
        return _respond(200, clock_doc())

    async def status_websocket(websocket: WebSocket) -> None:
        """Emulator-only status push (/_emulator/ws/status): the /status
        document every `interval` seconds until the client disconnects.
        Browsers cannot set an Authorization header on WebSockets, so the
        Basic token may come as ?token=<BASE64(user:SHA-256-hex(password))>.
        Needs a WS-capable server: pip install 'mir-emulator[ws]' (or
        uvicorn[standard]); the Lambda demo cannot hold sockets."""
        supplied = websocket.headers.get("authorization", "")
        query_token = websocket.query_params.get("token", "")
        if not supplied and query_token:
            supplied = f"Basic {query_token}"
        if emulator.enforce_auth and not auth.is_authorized(
            supplied, emulator.username, emulator.password
        ):
            await websocket.close(code=4401)
            return
        session_id = websocket.headers.get(SESSION_HEADER, "") or websocket.query_params.get(
            "session", ""
        )
        if session_id and not SESSION_ID_RE.match(session_id):
            await websocket.close(code=4400)
            return
        try:
            interval = float(websocket.query_params.get("interval", "1.0"))
        except ValueError:
            await websocket.close(code=4400)
            return
        interval = min(max(interval, 0.1), 10.0)

        await websocket.accept()
        state = emulator.state_for(session_id)
        status_op = spec.operations.get(("GET", "/status"))
        try:
            while True:
                ctx = RequestCtx(
                    spec=spec,
                    state=state,
                    op=status_op or next(iter(spec.operations.values())),
                    path_params={},
                    query={},
                    body=None,
                    mission_duration=emulator.mission_duration,
                    seed_collection=lambda key, path: emulator._seed_collection(state, key, path),
                    session_id=session_id,
                )
                _status, doc = await get_status(ctx)
                await websocket.send_json(doc)
                await asyncio.sleep(interval)
        except WebSocketDisconnect:
            pass

    async def recorder_endpoint(request: Request) -> Response:
        """Emulator-only scenario recorder (/_emulator/recorder)."""
        if not emulator._authorized(request):
            return _respond(401, _error_body(401, "Not authorized"))
        session_id = request.headers.get(SESSION_HEADER, "")
        if session_id and not SESSION_ID_RE.match(session_id):
            return _respond(
                400, _error_body(400, "Invalid X-MiR-Session: 1-64 chars from [A-Za-z0-9._-]")
            )
        state = emulator.state_for(session_id)
        if request.method == "DELETE":
            clear_recording(state)
        elif request.method == "PUT":
            raw = await request.body()
            if len(raw) > MAX_BODY_BYTES:
                return _respond(400, _error_body(400, "Payload too large"))
            try:
                body = json.loads(raw) if raw else {}
            except ValueError:
                return _respond(400, _error_body(400, "Invalid JSON"))
            if not isinstance(body, dict) or not isinstance(body.get("recording"), bool):
                return _respond(400, _error_body(400, 'Body must be {"recording": true|false}'))
            set_recording(state, body["recording"])
        doc = scenario_doc(state, version=version, family="robot")
        doc["replay"] = "save this document; mir-emulator --replay <file> re-runs it"
        return _respond(200, doc)

    async def not_found(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(_error_body(404, "Not found"), status_code=404)

    async def method_not_allowed(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(_error_body(405, "Method not allowed"), status_code=405)

    middleware = [Middleware(_SecurityHeadersMiddleware)]
    if cors:
        middleware.append(
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            )
        )

    app = Starlette(
        routes=[
            Route("/", index),
            Route("/swagger.json", swagger_json),
            Route("/openapi.json", openapi_json),
            Route("/_emulator/faults", faults_endpoint, methods=["GET", "PUT", "DELETE"]),
            Route("/_emulator/battery", battery_endpoint, methods=["GET", "PUT", "DELETE"]),
            Route("/_emulator/clock", clock_endpoint, methods=["GET", "PUT", "DELETE"]),
            Route("/_emulator/recorder", recorder_endpoint, methods=["GET", "PUT", "DELETE"]),
            WebSocketRoute("/_emulator/ws/status", status_websocket),
            *routes,
        ],
        exception_handlers={404: not_found, 405: method_not_allowed},
        middleware=middleware,
    )
    app.state.emulator = emulator
    app.state.mir_version = version
    return app
