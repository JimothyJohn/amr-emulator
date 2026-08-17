"""Validation against the vendored MassRobotics AMR Interop Standard schema.

The schema is vendored verbatim from MassRobotics-AMR/AMR_Interop_Standard
(see ``schemas/registry.json`` for commit and hashes). Every message this
emulator sends — and every message the receiver accepts — runs through it.
Outgoing violations raise: an emulator publishing a message its own oracle
rejects has a bug, and a crash surfaces that during development instead of
in someone's integration.
"""

from __future__ import annotations

import json
from functools import cache
from importlib import resources

import jsonschema


@cache
def schema() -> dict:
    root = resources.files("massrobotics_emulator.schemas")
    return json.loads((root / "AMR_Interop_Standard.json").read_text())


@cache
def _validator(fragment: str | None = None) -> jsonschema.protocols.Validator:
    doc = dict(schema())
    if fragment is not None:
        # The schema keeps identityReport/statusReport as root-level keys and
        # selects between them with a root oneOf; validating against one
        # fragment directly gives error messages that name the actual problem
        # instead of "not valid under any of the given schemas".
        doc = {"definitions": doc["definitions"], **doc[fragment]}
    # No $schema key upstream; the reference receiver compiles it with Ajv
    # defaults, which match draft-07 semantics.
    cls = jsonschema.validators.validator_for(doc, default=jsonschema.Draft7Validator)
    cls.check_schema(doc)
    return cls(doc)


def validation_errors(message: object, kind: str | None = None) -> list[str]:
    """Schema violations as readable strings (empty list = valid).

    ``kind`` is ``"identityReport"`` or ``"statusReport"`` for precise
    fragment errors, or ``None`` to check against the root oneOf exactly as
    the reference receiver does.
    """
    errors = []
    for error in _validator(kind).iter_errors(message):
        where = "/".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{where}: {error.message}")
    return sorted(errors)


def validate_outgoing(message: object, kind: str) -> None:
    """Hard-fail on any egress message the official schema rejects."""
    problems = validation_errors(message, kind)
    if problems:
        raise ProtocolViolation(kind, problems)


class ProtocolViolation(Exception):
    """An outgoing message failed validation against the official schema."""

    def __init__(self, kind: str, problems: list[str]) -> None:
        super().__init__(f"{kind} fails the official schema: {'; '.join(problems)}")
        self.kind = kind
        self.problems = problems
