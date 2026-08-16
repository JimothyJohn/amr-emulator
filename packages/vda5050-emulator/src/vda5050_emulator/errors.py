"""Error bookkeeping with the report-duration rules of Table 9.

Every predefined error type carries a retention policy ("until new order is
accepted", "until localization is regained", ...). Retention is modeled as a
clear-condition tag checked by the robot whenever the corresponding event
happens, so errors disappear exactly when the recommendation says they should.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Clear(Enum):
    NEW_ORDER = "new order accepted"
    NEW_INSTANT_ACTION = "new instant action accepted"
    NEW_MAP_ACTION = "new map-related instant action accepted"
    CONDITION = "cleared when the causing condition ends"
    MANUAL = "cleared explicitly"


# errorType -> (errorLevel, clear condition) for the predefined types (Table 9).
PREDEFINED: dict[str, tuple[str, Clear]] = {
    "UNSUPPORTED_PARAMETER": ("CRITICAL", Clear.NEW_ORDER),
    "NO_ORDER_TO_CANCEL": ("WARNING", Clear.NEW_ORDER),
    "VALIDATION_FAILURE": ("WARNING", Clear.NEW_ORDER),
    "INVALID_ORDER_ACTION": ("WARNING", Clear.NEW_ORDER),
    "INVALID_INSTANT_ACTION": ("WARNING", Clear.NEW_INSTANT_ACTION),
    "OUTDATED_ORDER_UPDATE": ("WARNING", Clear.NEW_ORDER),
    "SAME_ORDER_UPDATE_ID": ("WARNING", Clear.NEW_ORDER),
    "ORDER_UPDATE_FOLLOWING_CANCEL": ("WARNING", Clear.NEW_ORDER),
    "OUTSIDE_OF_CORRIDOR": ("CRITICAL", Clear.CONDITION),
    "INSUFFICIENT_MEMORY": ("URGENT", Clear.NEW_ORDER),
    "DUPLICATE_MAP": ("WARNING", Clear.NEW_MAP_ACTION),
    "BLOCKED_ZONE_VIOLATION": ("CRITICAL", Clear.CONDITION),
    "DUPLICATE_ZONE_SET": ("WARNING", Clear.NEW_MAP_ACTION),
    "RELEASE_LOST": ("CRITICAL", Clear.CONDITION),
    "ZONE_ACTION_CONFLICT": ("CRITICAL", Clear.CONDITION),
    "NODE_UNREACHABLE": ("CRITICAL", Clear.NEW_ORDER),
    "LOCALIZATION_ERROR": ("FATAL", Clear.CONDITION),
    "NO_ROUTE_TO_TARGET": ("WARNING", Clear.NEW_ORDER),
    "OTHER_ORDER_ACTIVE": ("WARNING", Clear.NEW_ORDER),
    "START_NODE_OUT_OF_RANGE": ("WARNING", Clear.NEW_ORDER),
    "MOBILE_ROBOT_NOT_AVAILABLE": ("WARNING", Clear.CONDITION),
    "UNKNOWN_MAP_ID": ("WARNING", Clear.NEW_ORDER),
    "INSTANT_ACTION_STATES_FULL": ("URGENT", Clear.CONDITION),
    "ZONE_ACTION_STATES_FULL": ("URGENT", Clear.CONDITION),
}


@dataclass
class ErrorEntry:
    error_type: str
    references: dict[str, str] = field(default_factory=dict)
    description: str = ""
    hint: str = ""
    level: str | None = None
    clear: Clear | None = None
    condition_key: str = ""  # discriminates CONDITION errors, e.g. zoneId

    def as_json(self) -> dict:
        level, _clear = PREDEFINED.get(self.error_type, ("WARNING", Clear.NEW_ORDER))
        doc: dict = {
            "errorType": self.error_type,
            "errorLevel": self.level or level,
        }
        if self.references:
            doc["errorReferences"] = [
                {"referenceKey": k, "referenceValue": str(v)} for k, v in self.references.items()
            ]
        if self.description:
            doc["errorDescription"] = self.description
        if self.hint:
            doc["errorHint"] = self.hint
        return doc


class ErrorBoard:
    """The state message's ``errors`` array plus retention bookkeeping."""

    def __init__(self) -> None:
        self._entries: list[ErrorEntry] = []

    def report(self, entry: ErrorEntry) -> None:
        if entry.clear is None:
            entry.clear = PREDEFINED.get(entry.error_type, ("WARNING", Clear.NEW_ORDER))[1]
        # A repeated report of the same type+references replaces the old one.
        self._entries = [
            e
            for e in self._entries
            if not (
                e.error_type == entry.error_type
                and e.references == entry.references
                and e.condition_key == entry.condition_key
            )
        ]
        self._entries.append(entry)

    def clear_for(self, event: Clear) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.clear is not event]
        return len(self._entries) != before

    def clear_condition(self, error_type: str, condition_key: str = "") -> bool:
        before = len(self._entries)
        self._entries = [
            e
            for e in self._entries
            if not (e.error_type == error_type and e.condition_key == condition_key)
        ]
        return len(self._entries) != before

    def active(self, error_type: str) -> bool:
        return any(e.error_type == error_type for e in self._entries)

    @property
    def fatal(self) -> bool:
        return any(e.as_json()["errorLevel"] == "FATAL" for e in self._entries)

    @property
    def order_blocking(self) -> bool:
        """CRITICAL or FATAL: the robot shall not continue driving its order."""
        return any(e.as_json()["errorLevel"] in ("CRITICAL", "FATAL") for e in self._entries)

    def as_json(self) -> list[dict]:
        return [e.as_json() for e in self._entries]
