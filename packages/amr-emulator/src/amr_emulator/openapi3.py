"""Swagger 2.0 -> OpenAPI 3.0 conversion for the subset MiR documents use.

Modern SDK generators and contract-testing tools increasingly refuse
Swagger 2.0; the emulator serves both flavors (/swagger.json and
/openapi.json) so it can slot into any toolchain. The conversion is validated
round-trip: the emulator's own OpenAPI 3 loader must produce the identical
operation table from the converted document (see tests).
"""

from __future__ import annotations

import copy
from typing import Any


def _rewrite_refs(node: Any) -> Any:
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                out[key] = value.replace("#/definitions/", "#/components/schemas/")
            else:
                out[key] = _rewrite_refs(value)
        return out
    if isinstance(node, list):
        return [_rewrite_refs(v) for v in node]
    return node


_PARAM_SCHEMA_KEYS = ("type", "format", "enum", "items", "minimum", "maximum", "default")


def _convert_parameter(param: dict) -> dict:
    out = {k: v for k, v in param.items() if k not in (*_PARAM_SCHEMA_KEYS, "schema")}
    schema = {k: param[k] for k in _PARAM_SCHEMA_KEYS if k in param}
    out["schema"] = schema or {"type": "string"}
    return out


def _convert_operation(op: dict, default_produces: list[str]) -> dict:
    out = {
        k: v for k, v in op.items() if k not in ("parameters", "responses", "produces", "consumes")
    }
    parameters = []
    request_body = None
    for param in op.get("parameters", []):
        if param.get("in") == "body":
            request_body = {
                "required": bool(param.get("required")),
                "content": {
                    "application/json": {"schema": param.get("schema") or {"type": "object"}}
                },
            }
            if param.get("description"):
                request_body["description"] = param["description"]
        else:
            parameters.append(_convert_parameter(param))
    if parameters:
        out["parameters"] = parameters
    if request_body:
        out["requestBody"] = request_body

    produces = op.get("produces") or default_produces or ["application/json"]
    responses = {}
    for code, response in op.get("responses", {}).items():
        converted = {"description": response.get("description", "")}
        schema = response.get("schema")
        if schema:
            content_type = produces[0] if produces else "application/json"
            converted["content"] = {content_type: {"schema": schema}}
        responses[str(code)] = converted
    out["responses"] = responses
    return out


def to_openapi3(swagger: dict) -> dict:
    """Convert a Swagger 2.0 document (MiR-shaped) to OpenAPI 3.0.3."""
    if swagger.get("swagger") != "2.0":
        raise ValueError("to_openapi3 expects a Swagger 2.0 document")
    doc = copy.deepcopy(swagger)
    default_produces = doc.get("produces") or ["application/json"]

    paths = {}
    for path, item in doc.get("paths", {}).items():
        converted_item = {}
        for method, op in item.items():
            if method in ("parameters", "$ref"):
                converted_item[method] = op
                continue
            converted_item[method] = _convert_operation(op, default_produces)
        paths[path] = converted_item

    out = {
        "openapi": "3.0.3",
        "info": doc.get("info", {}),
        "servers": [{"url": doc.get("basePath", "/api/v2.0.0")}],
        "paths": _rewrite_refs(paths),
        "components": {
            "schemas": _rewrite_refs(doc.get("definitions", {})),
            "securitySchemes": {"Basic": {"type": "http", "scheme": "basic"}},
        },
    }
    for passthrough in ("x-mir-converter-warnings",):
        if passthrough in doc:
            out[passthrough] = doc[passthrough]
    return out
