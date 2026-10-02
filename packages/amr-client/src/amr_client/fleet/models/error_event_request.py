from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ErrorEventRequest")


@_attrs_define
class ErrorEventRequest:
    """
    Attributes:
        action_type (str | Unset):
        entity_type (str | Unset):
        entity_id (str | Unset):
        error_type (str | Unset):
        message (str | Unset):
        timestamp (datetime.datetime | Unset):
    """

    action_type: str | Unset = UNSET
    entity_type: str | Unset = UNSET
    entity_id: str | Unset = UNSET
    error_type: str | Unset = UNSET
    message: str | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        action_type = self.action_type

        entity_type = self.entity_type

        entity_id = self.entity_id

        error_type = self.error_type

        message = self.message

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if action_type is not UNSET:
            field_dict["action-type"] = action_type
        if entity_type is not UNSET:
            field_dict["entity-type"] = entity_type
        if entity_id is not UNSET:
            field_dict["entity-id"] = entity_id
        if error_type is not UNSET:
            field_dict["error-type"] = error_type
        if message is not UNSET:
            field_dict["message"] = message
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action_type = d.pop("action-type", UNSET)

        entity_type = d.pop("entity-type", UNSET)

        entity_id = d.pop("entity-id", UNSET)

        error_type = d.pop("error-type", UNSET)

        message = d.pop("message", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        error_event_request = cls(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            error_type=error_type,
            message=message,
            timestamp=timestamp,
        )

        return error_event_request
