from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.alert import Alert
from ..types import UNSET, Unset

T = TypeVar("T", bound="AlertEventRequest")


@_attrs_define
class AlertEventRequest:
    """
    Attributes:
        id (str | Unset):
        name (Alert | Unset):
        message (str | Unset):
        timestamp (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    name: Alert | Unset = UNSET
    message: str | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name: str | Unset = UNSET
        if not isinstance(self.name, Unset):
            name = self.name.value

        message = self.message

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if message is not UNSET:
            field_dict["message"] = message
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _name = d.pop("name", UNSET)
        name: Alert | Unset
        if isinstance(_name, Unset):
            name = UNSET
        else:
            name = Alert(_name)

        message = d.pop("message", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        alert_event_request = cls(
            id=id,
            name=name,
            message=message,
            timestamp=timestamp,
        )

        return alert_event_request
