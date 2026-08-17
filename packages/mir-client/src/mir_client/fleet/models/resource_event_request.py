from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resource_event import ResourceEvent


T = TypeVar("T", bound="ResourceEventRequest")


@_attrs_define
class ResourceEventRequest:
    """
    Attributes:
        is_snapshot (bool | Unset):
        resource_events (list[ResourceEvent] | Unset):
        timestamp (datetime.datetime | Unset):
    """

    is_snapshot: bool | Unset = UNSET
    resource_events: list[ResourceEvent] | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_snapshot = self.is_snapshot

        resource_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.resource_events, Unset):
            resource_events = []
            for resource_events_item_data in self.resource_events:
                resource_events_item = resource_events_item_data.to_dict()
                resource_events.append(resource_events_item)

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_snapshot is not UNSET:
            field_dict["is-snapshot"] = is_snapshot
        if resource_events is not UNSET:
            field_dict["resource-events"] = resource_events
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_event import ResourceEvent

        d = dict(src_dict)
        is_snapshot = d.pop("is-snapshot", UNSET)

        _resource_events = d.pop("resource-events", UNSET)
        resource_events: list[ResourceEvent] | Unset = UNSET
        if _resource_events is not UNSET:
            resource_events = []
            for resource_events_item_data in _resource_events:
                resource_events_item = ResourceEvent.from_dict(resource_events_item_data)

                resource_events.append(resource_events_item)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        resource_event_request = cls(
            is_snapshot=is_snapshot,
            resource_events=resource_events,
            timestamp=timestamp,
        )

        return resource_event_request
