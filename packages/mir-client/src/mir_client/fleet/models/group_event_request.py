from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_event import GroupEvent


T = TypeVar("T", bound="GroupEventRequest")


@_attrs_define
class GroupEventRequest:
    """
    Attributes:
        is_snapshot (bool | Unset):
        group_events (list[GroupEvent] | Unset):
    """

    is_snapshot: bool | Unset = UNSET
    group_events: list[GroupEvent] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_snapshot = self.is_snapshot

        group_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.group_events, Unset):
            group_events = []
            for group_events_item_data in self.group_events:
                group_events_item = group_events_item_data.to_dict()
                group_events.append(group_events_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_snapshot is not UNSET:
            field_dict["is-snapshot"] = is_snapshot
        if group_events is not UNSET:
            field_dict["group-events"] = group_events

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_event import GroupEvent

        d = dict(src_dict)
        is_snapshot = d.pop("is-snapshot", UNSET)

        _group_events = d.pop("group-events", UNSET)
        group_events: list[GroupEvent] | Unset = UNSET
        if _group_events is not UNSET:
            group_events = []
            for group_events_item_data in _group_events:
                group_events_item = GroupEvent.from_dict(group_events_item_data)

                group_events.append(group_events_item)

        group_event_request = cls(
            is_snapshot=is_snapshot,
            group_events=group_events,
        )

        return group_event_request
