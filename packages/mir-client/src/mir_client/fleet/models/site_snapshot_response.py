from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.site_event import SiteEvent


T = TypeVar("T", bound="SiteSnapshotResponse")


@_attrs_define
class SiteSnapshotResponse:
    """
    Attributes:
        site_events (list[SiteEvent] | Unset):
    """

    site_events: list[SiteEvent] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        site_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.site_events, Unset):
            site_events = []
            for site_events_item_data in self.site_events:
                site_events_item = site_events_item_data.to_dict()
                site_events.append(site_events_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if site_events is not UNSET:
            field_dict["site-events"] = site_events

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.site_event import SiteEvent

        d = dict(src_dict)
        _site_events = d.pop("site-events", UNSET)
        site_events: list[SiteEvent] | Unset = UNSET
        if _site_events is not UNSET:
            site_events = []
            for site_events_item_data in _site_events:
                site_events_item = SiteEvent.from_dict(site_events_item_data)

                site_events.append(site_events_item)

        site_snapshot_response = cls(
            site_events=site_events,
        )

        return site_snapshot_response
