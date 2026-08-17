from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.serial_order_status_event import SerialOrderStatusEvent


T = TypeVar("T", bound="SerialOrderStatusEventRequest")


@_attrs_define
class SerialOrderStatusEventRequest:
    """
    Attributes:
        is_snapshot (bool | Unset):
        serial_order_status_events (list[SerialOrderStatusEvent] | Unset):
    """

    is_snapshot: bool | Unset = UNSET
    serial_order_status_events: list[SerialOrderStatusEvent] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_snapshot = self.is_snapshot

        serial_order_status_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.serial_order_status_events, Unset):
            serial_order_status_events = []
            for serial_order_status_events_item_data in self.serial_order_status_events:
                serial_order_status_events_item = serial_order_status_events_item_data.to_dict()
                serial_order_status_events.append(serial_order_status_events_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_snapshot is not UNSET:
            field_dict["is-snapshot"] = is_snapshot
        if serial_order_status_events is not UNSET:
            field_dict["serial-order-status-events"] = serial_order_status_events

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.serial_order_status_event import SerialOrderStatusEvent

        d = dict(src_dict)
        is_snapshot = d.pop("is-snapshot", UNSET)

        _serial_order_status_events = d.pop("serial-order-status-events", UNSET)
        serial_order_status_events: list[SerialOrderStatusEvent] | Unset = UNSET
        if _serial_order_status_events is not UNSET:
            serial_order_status_events = []
            for serial_order_status_events_item_data in _serial_order_status_events:
                serial_order_status_events_item = SerialOrderStatusEvent.from_dict(
                    serial_order_status_events_item_data
                )

                serial_order_status_events.append(serial_order_status_events_item)

        serial_order_status_event_request = cls(
            is_snapshot=is_snapshot,
            serial_order_status_events=serial_order_status_events,
        )

        return serial_order_status_event_request
