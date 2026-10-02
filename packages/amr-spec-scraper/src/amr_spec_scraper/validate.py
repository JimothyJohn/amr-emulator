"""Structural comparison of two swagger documents.

The correctness oracle for the PDF converter: MiR published exactly one
machine-readable spec (3.5.4 swagger.json); a conversion of the 3.5.4 PDF must
be structurally identical to it. Prose descriptions are ignored; an itemless
array and items {type: object} are treated as equal because the PDF renders
both as "< object > array".
"""

from __future__ import annotations

from typing import Any


def schema_signature(schema: dict | None) -> Any:
    if not schema:
        return None
    if "$ref" in schema:
        return ("ref", schema["$ref"].rsplit("/", 1)[-1])
    stype = schema.get("type")
    if stype == "array":
        items = schema_signature(schema.get("items"))
        if items == ("object", ()):
            items = None
        return ("array", items)
    if stype == "object" or "properties" in schema:
        props = schema.get("properties") or {}
        return ("object", tuple(sorted((k, schema_signature(v)) for k, v in props.items())))
    if "enum" in schema:
        return ("enum", tuple(schema["enum"]))
    return (stype, schema.get("format"))


def _op_signature(op: dict) -> dict:
    body = next((p.get("schema") for p in op.get("parameters", []) if p.get("in") == "body"), None)
    params = sorted(
        (p.get("in"), p.get("name"), p.get("type"))
        for p in op.get("parameters", [])
        if p.get("in") in ("path", "query", "formData")
    )
    responses = {
        code: schema_signature(r.get("schema"))
        for code, r in op.get("responses", {}).items()
        if str(code).isdigit()
    }
    return {
        "body": schema_signature(body),
        "params": params,
        "responses": responses,
        "produces": sorted(op.get("produces") or []),
    }


def compare(converted: dict, reference: dict) -> list[str]:
    """Human-readable structural differences; empty means equivalent."""
    problems: list[str] = []

    def ops(doc: dict) -> dict:
        return {
            (m.lower(), p): op
            for p, item in doc.get("paths", {}).items()
            for m, op in item.items()
            if m.lower() in ("get", "post", "put", "delete", "patch")
        }

    conv_ops, ref_ops = ops(converted), ops(reference)
    for key in sorted(set(ref_ops) - set(conv_ops)):
        problems.append(f"missing operation: {key[0].upper()} {key[1]}")
    for key in sorted(set(conv_ops) - set(ref_ops)):
        problems.append(f"extra operation: {key[0].upper()} {key[1]}")
    for key in sorted(set(conv_ops) & set(ref_ops)):
        a, b = _op_signature(conv_ops[key]), _op_signature(ref_ops[key])
        for field in ("body", "params", "responses", "produces"):
            if a[field] != b[field]:
                problems.append(
                    f"{key[0].upper()} {key[1]} {field}: "
                    f"converted={a[field]!r} reference={b[field]!r}"
                )

    conv_defs = converted.get("definitions", {})
    ref_defs = reference.get("definitions", {})
    for name in sorted(set(ref_defs) - set(conv_defs)):
        problems.append(f"missing definition: {name}")
    for name in sorted(set(conv_defs) - set(ref_defs)):
        problems.append(f"extra definition: {name}")
    for name in sorted(set(conv_defs) & set(ref_defs)):
        sig_a, sig_b = schema_signature(conv_defs[name]), schema_signature(ref_defs[name])
        if sig_a != sig_b:
            problems.append(f"definition {name}: converted={sig_a!r} reference={sig_b!r}")

    problems.extend(converted.get("x-mir-converter-warnings", []))
    return problems
