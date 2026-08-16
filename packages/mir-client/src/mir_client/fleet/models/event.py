from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_payload import EventPayload


T = TypeVar("T", bound="Event")


@_attrs_define
class Event:
    """
    Attributes:
        name (str | Unset):
        payload (EventPayload | Unset):
        robot_id (str | Unset):
        serial_order_id (str | Unset):
        phase_index (int | None | Unset):
        is_fallback (bool | None | Unset):
        timestamp (datetime.datetime | Unset):
    """

    name: str | Unset = UNSET
    payload: EventPayload | Unset = UNSET
    robot_id: str | Unset = UNSET
    serial_order_id: str | Unset = UNSET
    phase_index: int | None | Unset = UNSET
    is_fallback: bool | None | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        payload: dict[str, Any] | Unset = UNSET
        if not isinstance(self.payload, Unset):
            payload = self.payload.to_dict()

        robot_id = self.robot_id

        serial_order_id = self.serial_order_id

        phase_index: int | None | Unset
        if isinstance(self.phase_index, Unset):
            phase_index = UNSET
        else:
            phase_index = self.phase_index

        is_fallback: bool | None | Unset
        if isinstance(self.is_fallback, Unset):
            is_fallback = UNSET
        else:
            is_fallback = self.is_fallback

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if payload is not UNSET:
            field_dict["payload"] = payload
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id
        if serial_order_id is not UNSET:
            field_dict["serial-order-id"] = serial_order_id
        if phase_index is not UNSET:
            field_dict["phase-index"] = phase_index
        if is_fallback is not UNSET:
            field_dict["is-fallback"] = is_fallback
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_payload import EventPayload

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _payload = d.pop("payload", UNSET)
        payload: EventPayload | Unset
        if isinstance(_payload, Unset):
            payload = UNSET
        else:
            payload = EventPayload.from_dict(_payload)

        robot_id = d.pop("robot-id", UNSET)

        serial_order_id = d.pop("serial-order-id", UNSET)

        def _parse_phase_index(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        phase_index = _parse_phase_index(d.pop("phase-index", UNSET))

        def _parse_is_fallback(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_fallback = _parse_is_fallback(d.pop("is-fallback", UNSET))

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        event = cls(
            name=name,
            payload=payload,
            robot_id=robot_id,
            serial_order_id=serial_order_id,
            phase_index=phase_index,
            is_fallback=is_fallback,
            timestamp=timestamp,
        )

        return event
