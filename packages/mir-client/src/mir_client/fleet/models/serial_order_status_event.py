from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.order_state import OrderState
from ..types import UNSET, Unset

T = TypeVar("T", bound="SerialOrderStatusEvent")


@_attrs_define
class SerialOrderStatusEvent:
    """
    Attributes:
        serial_order_id (str | Unset):
        phase_index (int | None | Unset):
        mission_id (None | str | Unset):
        state (OrderState | Unset):
        state_change_timestamp (datetime.datetime | Unset):
        robot_id (str | Unset):
        message (None | str | Unset):
        is_fallback (bool | None | Unset):
        order_type (str | Unset):
    """

    serial_order_id: str | Unset = UNSET
    phase_index: int | None | Unset = UNSET
    mission_id: None | str | Unset = UNSET
    state: OrderState | Unset = UNSET
    state_change_timestamp: datetime.datetime | Unset = UNSET
    robot_id: str | Unset = UNSET
    message: None | str | Unset = UNSET
    is_fallback: bool | None | Unset = UNSET
    order_type: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        serial_order_id = self.serial_order_id

        phase_index: int | None | Unset
        if isinstance(self.phase_index, Unset):
            phase_index = UNSET
        else:
            phase_index = self.phase_index

        mission_id: None | str | Unset
        if isinstance(self.mission_id, Unset):
            mission_id = UNSET
        else:
            mission_id = self.mission_id

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        state_change_timestamp: str | Unset = UNSET
        if not isinstance(self.state_change_timestamp, Unset):
            state_change_timestamp = self.state_change_timestamp.isoformat()

        robot_id = self.robot_id

        message: None | str | Unset
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        is_fallback: bool | None | Unset
        if isinstance(self.is_fallback, Unset):
            is_fallback = UNSET
        else:
            is_fallback = self.is_fallback

        order_type = self.order_type

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if serial_order_id is not UNSET:
            field_dict["serial-order-id"] = serial_order_id
        if phase_index is not UNSET:
            field_dict["phase-index"] = phase_index
        if mission_id is not UNSET:
            field_dict["mission-id"] = mission_id
        if state is not UNSET:
            field_dict["state"] = state
        if state_change_timestamp is not UNSET:
            field_dict["state-change-timestamp"] = state_change_timestamp
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id
        if message is not UNSET:
            field_dict["message"] = message
        if is_fallback is not UNSET:
            field_dict["is-fallback"] = is_fallback
        if order_type is not UNSET:
            field_dict["order-type"] = order_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        serial_order_id = d.pop("serial-order-id", UNSET)

        def _parse_phase_index(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        phase_index = _parse_phase_index(d.pop("phase-index", UNSET))

        def _parse_mission_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mission_id = _parse_mission_id(d.pop("mission-id", UNSET))

        _state = d.pop("state", UNSET)
        state: OrderState | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = OrderState(_state)

        _state_change_timestamp = d.pop("state-change-timestamp", UNSET)
        state_change_timestamp: datetime.datetime | Unset
        if isinstance(_state_change_timestamp, Unset):
            state_change_timestamp = UNSET
        else:
            state_change_timestamp = datetime.datetime.fromisoformat(_state_change_timestamp)

        robot_id = d.pop("robot-id", UNSET)

        def _parse_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_is_fallback(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_fallback = _parse_is_fallback(d.pop("is-fallback", UNSET))

        order_type = d.pop("order-type", UNSET)

        serial_order_status_event = cls(
            serial_order_id=serial_order_id,
            phase_index=phase_index,
            mission_id=mission_id,
            state=state,
            state_change_timestamp=state_change_timestamp,
            robot_id=robot_id,
            message=message,
            is_fallback=is_fallback,
            order_type=order_type,
        )

        return serial_order_status_event
