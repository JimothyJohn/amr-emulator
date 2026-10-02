"""Deterministic example values synthesized from (dereferenced) JSON schemas.

No randomness: the same schema always yields the same value, so emulator
responses are reproducible across runs and safe to assert against in tests.
"""

from __future__ import annotations

from typing import Any

_STRING_FORMATS = {
    "date-time": "2020-01-01T00:00:00Z",
    "date": "2020-01-01",
    "byte": "ZW11bGF0b3I=",
    "uri": "http://mir.example/api/v2.0.0/",
}

_NAME_HINTS = {
    "guid": "emulated-0000-0000-0000-000000000000",
    "url": "/v2.0.0/",
    "name": "emulated",
}


def overlay_compatible(base: dict, overrides: dict) -> dict:
    """Copy override values onto *base*, but only for keys that already exist
    there with a compatible type — keeps schema-derived documents valid when
    merging client-supplied or differently-shaped data."""
    for key, value in overrides.items():
        if key not in base:
            continue
        current = base[key]
        if (
            current is None
            or isinstance(value, type(current))
            or (isinstance(current, float) and isinstance(value, int | float))
        ):
            base[key] = float(value) if isinstance(current, float) else value
    return base


def example_from_schema(schema: dict | None, name: str = "", depth: int = 16) -> Any:
    """Build a value that satisfies *schema* (already $ref-free, see Spec.deref)."""
    if not schema or depth <= 0:
        return {}

    if schema.get("enum"):
        return schema["enum"][0]
    if "default" in schema:
        return schema["default"]

    if "allOf" in schema:
        merged: dict = {}
        for part in schema["allOf"]:
            if isinstance(part, dict):
                merged.update(part)
        return example_from_schema(merged, name, depth - 1)
    for combinator in ("anyOf", "oneOf"):
        options = schema.get(combinator)
        if options:
            return example_from_schema(options[0], name, depth - 1)

    stype = schema.get("type")
    if isinstance(stype, list):
        stype = stype[0] if stype else None
    if stype is None and "properties" in schema:
        stype = "object"
    if stype is None and "items" in schema:
        stype = "array"

    if stype == "object" or stype is None:
        props = schema.get("properties") or {}
        return {k: example_from_schema(v, k, depth - 1) for k, v in props.items()}
    if stype == "array":
        items = schema.get("items")
        if not items:
            return []
        min_items = schema.get("minItems", 1)
        value = example_from_schema(items, name, depth - 1)
        return [value] * max(1, min(min_items, 3))
    if stype == "string":
        fmt = schema.get("format")
        if fmt in _STRING_FORMATS:
            return _STRING_FORMATS[fmt]
        lowered = name.lower()
        for hint, value in _NAME_HINTS.items():
            if hint in lowered:
                return value
        if schema.get("minLength"):
            return "e" * schema["minLength"]
        return "emulated"
    if stype == "integer":
        return schema.get("minimum", 0)
    if stype == "number":
        return float(schema.get("minimum", 0.0))
    if stype == "boolean":
        return False
    if stype == "null":
        return None
    return {}
