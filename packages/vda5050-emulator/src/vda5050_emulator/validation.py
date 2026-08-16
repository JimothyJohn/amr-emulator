"""Message validation against the bundled official VDA 5050 JSON schemas.

The schemas are vendored verbatim from the public VDA5050/VDA5050 repository
(see ``schemas/registry.json`` for tag, commit and hashes; the only accepted
normalization is stripping upstream trailing commas —
``scripts/sync_vda5050_schemas.py``). Every message the emulator publishes and
every message it receives runs through these validators.
"""

from __future__ import annotations

import json
from functools import cache
from importlib import resources

import jsonschema

SCHEMA_TAG = "3.0.0"
MESSAGE_TYPES = (
    "connection",
    "factsheet",
    "instantActions",
    "order",
    "responses",
    "state",
    "visualization",
    "zoneSet",
)


@cache
def schema(message_type: str, tag: str = SCHEMA_TAG) -> dict:
    if message_type not in MESSAGE_TYPES:
        raise KeyError(f"unknown VDA 5050 message type: {message_type!r}")
    root = resources.files("vda5050_emulator.schemas")
    return json.loads((root / f"v{tag}" / f"{message_type}.schema.json").read_text())


@cache
def _validator(message_type: str, tag: str = SCHEMA_TAG) -> jsonschema.protocols.Validator:
    doc = schema(message_type, tag)
    cls = jsonschema.validators.validator_for(doc)
    cls.check_schema(doc)
    return cls(doc)


def validation_errors(message_type: str, message: object, tag: str = SCHEMA_TAG) -> list[str]:
    """All schema violations as human-readable strings (empty list = valid)."""
    errors = []
    for err in _validator(message_type, tag).iter_errors(message):
        path = "$" + "".join(f"[{p!r}]" for p in err.absolute_path)
        errors.append(f"{path}: {err.message}")
    return errors


def registry() -> dict:
    root = resources.files("vda5050_emulator.schemas")
    return json.loads((root / "registry.json").read_text())
