"""Load Swagger 2.0 / OpenAPI 3.x documents into one normalized model.

The official MiR portal ships Swagger 2.0 files; the community 2.7.0 seed is
OpenAPI 3.0. The emulator only needs a uniform view: operations with path
templates, parameters, an optional JSON body schema, and per-status response
schemas, plus a resolver for $ref lookups into the source document.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

MAX_REF_DEPTH = 12


@dataclass(frozen=True)
class Operation:
    method: str  # upper-case HTTP method
    path: str  # template relative to base_path, e.g. "/mission_queue/{id}"
    params: tuple[dict, ...]  # parameter objects (path + query), swagger-2 style
    body_schema: dict | None
    body_required: bool
    responses: dict[int, dict | None]  # status -> (unresolved) schema
    produces: tuple[str, ...] = ("application/json",)

    @property
    def success_status(self) -> int:
        ok = sorted(s for s in self.responses if 200 <= s < 300)
        return ok[0] if ok else 200

    @property
    def success_schema(self) -> dict | None:
        return self.responses.get(self.success_status)

    def path_param_types(self) -> dict[str, str]:
        return {p["name"]: p.get("type", "string") for p in self.params if p.get("in") == "path"}


@dataclass
class Spec:
    mir_version: str
    title: str
    base_path: str
    operations: dict[tuple[str, str], Operation]
    document: dict = field(repr=False)

    def resolve_ref(self, ref: str) -> dict:
        node: Any = self.document
        if not ref.startswith("#/"):
            raise ValueError(f"only local $refs are supported, got {ref!r}")
        for part in ref[2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
        return node

    def deref(self, schema: dict | None, depth: int = MAX_REF_DEPTH) -> dict:
        """Return a self-contained copy of *schema* with $refs inlined.

        Cyclic or overly deep references collapse to the permissive schema {}.
        """
        if not schema:
            return {}
        if depth <= 0:
            return {}
        if "$ref" in schema:
            return self.deref(self.resolve_ref(schema["$ref"]), depth - 1)
        out: dict = {}
        for key, value in schema.items():
            if key in ("properties", "patternProperties") and isinstance(value, dict):
                out[key] = {k: self.deref(v, depth - 1) for k, v in value.items()}
            elif key in ("items", "additionalProperties", "not") and isinstance(value, dict):
                out[key] = self.deref(value, depth - 1)
            elif key in ("allOf", "anyOf", "oneOf") and isinstance(value, list):
                out[key] = [self.deref(v, depth - 1) for v in value]
            else:
                out[key] = value
        return out


def _swagger2_operations(doc: dict) -> dict[tuple[str, str], Operation]:
    ops: dict[tuple[str, str], Operation] = {}
    for path, item in doc.get("paths", {}).items():
        shared = item.get("parameters", [])
        for method, op in item.items():
            if method == "parameters" or not isinstance(op, dict):
                continue
            params = [*shared, *op.get("parameters", [])]
            body = next((p for p in params if p.get("in") == "body"), None)
            responses = {}
            for code, resp in op.get("responses", {}).items():
                if str(code).isdigit():
                    responses[int(code)] = resp.get("schema") if isinstance(resp, dict) else None
            ops[(method.upper(), path)] = Operation(
                method=method.upper(),
                path=path,
                params=tuple(p for p in params if p.get("in") in ("path", "query")),
                body_schema=body.get("schema") if body else None,
                body_required=bool(body and body.get("required")),
                responses=responses,
                produces=tuple(op.get("produces") or doc.get("produces") or ["application/json"]),
            )
    return ops


def _openapi3_operations(doc: dict) -> dict[tuple[str, str], Operation]:
    ops: dict[tuple[str, str], Operation] = {}
    for path, item in doc.get("paths", {}).items():
        shared = item.get("parameters", [])
        for method, op in item.items():
            if method in ("parameters", "servers") or not isinstance(op, dict):
                continue
            raw_params = [*shared, *op.get("parameters", [])]
            params = []
            for p in raw_params:
                if p.get("in") not in ("path", "query"):
                    continue
                q = {k: v for k, v in p.items() if k != "schema"}
                q["type"] = (p.get("schema") or {}).get("type", "string")
                params.append(q)
            body_schema = None
            body_required = False
            request_body = op.get("requestBody") or {}
            content = request_body.get("content") or {}
            for ctype, media in content.items():
                if "json" in ctype:
                    body_schema = media.get("schema")
                    body_required = bool(request_body.get("required"))
                    break
            responses: dict[int, dict | None] = {}
            produces: list[str] = []
            for code, resp in (op.get("responses") or {}).items():
                if not str(code).isdigit():
                    continue
                schema = None
                for ctype, media in (resp.get("content") or {}).items():
                    produces.append(ctype)
                    if "json" in ctype:
                        schema = media.get("schema")
                responses[int(code)] = schema
            ops[(method.upper(), path)] = Operation(
                method=method.upper(),
                path=path,
                params=tuple(params),
                body_schema=body_schema,
                body_required=body_required,
                responses=responses,
                produces=tuple(dict.fromkeys(produces)) or ("application/json",),
            )
    return ops


def load_spec(path: Path, mir_version: str) -> Spec:
    text = path.read_text()
    doc = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)

    if doc.get("swagger") == "2.0":
        operations = _swagger2_operations(doc)
        base_path = doc.get("basePath", "/api/v2.0.0")
    elif str(doc.get("openapi", "")).startswith("3"):
        operations = _openapi3_operations(doc)
        servers = doc.get("servers") or []

        # Documents whose path keys are already absolute (the Fleet APIs write
        # /api/v1/... or /compatibility_api/v1/... into paths) need no prefix;
        # robot-shaped docs with relative keys (/status) keep the MiR base path.
        def _absolute(path: str) -> bool:
            head = path.split("/")[1] if "/" in path else ""
            return head == "api" or head.endswith("_api")

        paths_absolute = any(_absolute(p) for p in doc.get("paths", {}))
        base_path = "" if paths_absolute else "/api/v2.0.0"
        if servers:
            url = servers[0].get("url", "")
            _, _, tail = url.partition("//")
            slash = tail.find("/")
            if slash >= 0 and tail[slash:] != "/":
                base_path = tail[slash:].rstrip("/")
    else:
        raise ValueError(f"unrecognized API document at {path}")

    info = doc.get("info", {})
    return Spec(
        mir_version=mir_version,
        title=info.get("title", "MiR REST API"),
        base_path=base_path,
        operations=operations,
        document=doc,
    )
