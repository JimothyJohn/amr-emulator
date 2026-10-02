"""Structural API diff between two tracked spec versions, at runtime.

Lets integrators preflight an upgrade: GET /_emulator/diff?from=2.14.7&to=3.8.1
on the dispatcher returns which operations and definitions were added, removed,
or changed shape. "Changed" is structural — parameter names/types, body and
response schemas — never descriptions, so the pinned 3.5.4 oracle diffs clean
against the converted 3.5.6 exactly like the scraper's changelog does.

Works within one family at a time (robot↔robot or fleet↔fleet); the two
families are different APIs and a cross diff would be noise.
"""

from __future__ import annotations

from typing import Any

from amr_emulator import registry
from amr_emulator.spec import Operation, Spec, load_spec


def schema_signature(schema: Any, depth: int = 12) -> Any:
    """Hashable structural fingerprint of a (deref'd) schema.

    Deliberately the same granularity as the scraper's conversion oracle
    (amr_spec_scraper.validate.schema_signature): type/format/enum/properties
    only. The MiR PDFs cannot carry `required`, numeric bounds, or
    additionalProperties, so a finer signature would report the conversion
    pipeline's information loss as API changes — e.g. the pinned official
    3.5.4 vs the converted 3.5.6, which are structurally the same API.
    """
    if not isinstance(schema, dict) or not schema or depth <= 0:
        return None
    stype = schema.get("type")
    if stype == "array":
        items = schema_signature(schema.get("items"), depth - 1)
        if items == ("object", ()):
            items = None  # itemless array and object-array render identically
        return ("array", items)
    if stype == "object" or "properties" in schema:
        props = schema.get("properties") or {}
        return (
            "object",
            tuple(sorted((k, schema_signature(v, depth - 1)) for k, v in props.items())),
        )
    if "enum" in schema:
        return ("enum", tuple(str(v) for v in schema["enum"]))
    return (stype, schema.get("format"))


def _op_signature(spec: Spec, op: Operation) -> Any:
    params = tuple(
        sorted((p.get("in", ""), p.get("name", ""), p.get("type", "")) for p in op.params)
    )
    body = schema_signature(spec.deref(op.body_schema)) if op.body_schema else None
    responses = tuple(
        sorted(
            (status, schema_signature(spec.deref(schema)) if schema else None)
            for status, schema in op.responses.items()
        )
    )
    return (params, body, responses, tuple(sorted(op.produces)))


def _definitions(spec: Spec) -> dict[str, dict]:
    doc = spec.document
    return doc.get("definitions") or (doc.get("components") or {}).get("schemas") or {}


def api_diff(old: Spec, new: Spec) -> dict:
    """JSON-ready structural diff old → new."""
    old_ops, new_ops = old.operations, new.operations
    added = sorted(set(new_ops) - set(old_ops))
    removed = sorted(set(old_ops) - set(new_ops))
    changed = sorted(
        key
        for key in set(old_ops) & set(new_ops)
        if _op_signature(old, old_ops[key]) != _op_signature(new, new_ops[key])
    )

    old_defs, new_defs = _definitions(old), _definitions(new)
    defs_added = sorted(set(new_defs) - set(old_defs))
    defs_removed = sorted(set(old_defs) - set(new_defs))
    defs_changed = sorted(
        name
        for name in set(old_defs) & set(new_defs)
        if schema_signature(old.deref(old_defs[name]))
        != schema_signature(new.deref(new_defs[name]))
    )

    render = [f"{method} {path}" for method, path in (*added, *removed, *changed)]
    return {
        "from": old.mir_version,
        "to": new.mir_version,
        "operations": {
            "added": [f"{m} {p}" for m, p in added],
            "removed": [f"{m} {p}" for m, p in removed],
            "changed": [f"{m} {p}" for m, p in changed],
        },
        "definitions": {
            "added": defs_added,
            "removed": defs_removed,
            "changed": defs_changed,
        },
        "structurally_identical": not (render or defs_added or defs_removed or defs_changed),
    }


def diff_versions(from_version: str, to_version: str) -> dict:
    """Diff two tracked versions of the same family.

    Raises KeyError for unknown versions and ValueError for a cross-family mix.
    """
    robot = set(registry.supported_versions())
    fleet = set(registry.fleet_supported_versions())

    def family(version: str) -> str:
        if version in robot:
            return "robot"
        if version in fleet:
            return "fleet"
        raise KeyError(
            f"version {version!r} is not tracked; robot: {sorted(robot)}, fleet: {sorted(fleet)}"
        )

    from_family, to_family = family(from_version), family(to_version)
    if from_family != to_family:
        raise ValueError(
            f"{from_version} is a {from_family} version but {to_version} is a "
            f"{to_family} version; diff within one API family"
        )
    loader = registry.spec_path if from_family == "robot" else registry.fleet_spec_path
    old = load_spec(loader(from_version)[1], from_version)
    new = load_spec(loader(to_version)[1], to_version)
    result = api_diff(old, new)
    result["family"] = from_family
    return result
