from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.system_event import SystemEvent


T = TypeVar("T", bound="SystemEventRequest")


@_attrs_define
class SystemEventRequest:
    """
    Attributes:
        is_snapshot (bool | Unset):
        system_events (list[SystemEvent] | Unset):
    """

    is_snapshot: bool | Unset = UNSET
    system_events: list[SystemEvent] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_snapshot = self.is_snapshot

        system_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.system_events, Unset):
            system_events = []
            for system_events_item_data in self.system_events:
                system_events_item = system_events_item_data.to_dict()
                system_events.append(system_events_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_snapshot is not UNSET:
            field_dict["is-snapshot"] = is_snapshot
        if system_events is not UNSET:
            field_dict["system-events"] = system_events

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.system_event import SystemEvent

        d = dict(src_dict)
        is_snapshot = d.pop("is-snapshot", UNSET)

        _system_events = d.pop("system-events", UNSET)
        system_events: list[SystemEvent] | Unset = UNSET
        if _system_events is not UNSET:
            system_events = []
            for system_events_item_data in _system_events:
                system_events_item = SystemEvent.from_dict(system_events_item_data)

                system_events.append(system_events_item)

        system_event_request = cls(
            is_snapshot=is_snapshot,
            system_events=system_events,
        )

        return system_event_request
