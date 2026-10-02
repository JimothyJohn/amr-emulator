from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..models.serial_order_priority import SerialOrderPriority
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateSerialOrderRequest")


@_attrs_define
class UpdateSerialOrderRequest:
    """
    Attributes:
        serial_order_id (UUID):
        priority (SerialOrderPriority | Unset):
        earliest_start_time (datetime.datetime | None | Unset):
        robot_id (None | Unset | UUID):
    """

    serial_order_id: UUID
    priority: SerialOrderPriority | Unset = UNSET
    earliest_start_time: datetime.datetime | None | Unset = UNSET
    robot_id: None | Unset | UUID = UNSET

    def to_dict(self) -> dict[str, Any]:
        serial_order_id = str(self.serial_order_id)

        priority: str | Unset = UNSET
        if not isinstance(self.priority, Unset):
            priority = self.priority.value

        earliest_start_time: None | str | Unset
        if isinstance(self.earliest_start_time, Unset):
            earliest_start_time = UNSET
        elif isinstance(self.earliest_start_time, datetime.datetime):
            earliest_start_time = self.earliest_start_time.isoformat()
        else:
            earliest_start_time = self.earliest_start_time

        robot_id: None | str | Unset
        if isinstance(self.robot_id, Unset):
            robot_id = UNSET
        elif isinstance(self.robot_id, UUID):
            robot_id = str(self.robot_id)
        else:
            robot_id = self.robot_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "serial-order-id": serial_order_id,
            }
        )
        if priority is not UNSET:
            field_dict["priority"] = priority
        if earliest_start_time is not UNSET:
            field_dict["earliest-start-time"] = earliest_start_time
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        serial_order_id = UUID(d.pop("serial-order-id"))

        _priority = d.pop("priority", UNSET)
        priority: SerialOrderPriority | Unset
        if isinstance(_priority, Unset):
            priority = UNSET
        else:
            priority = SerialOrderPriority(_priority)

        def _parse_earliest_start_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                earliest_start_time_type_0 = datetime.datetime.fromisoformat(data)

                return earliest_start_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        earliest_start_time = _parse_earliest_start_time(d.pop("earliest-start-time", UNSET))

        def _parse_robot_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                robot_id_type_0 = UUID(data)

                return robot_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        robot_id = _parse_robot_id(d.pop("robot-id", UNSET))

        update_serial_order_request = cls(
            serial_order_id=serial_order_id,
            priority=priority,
            earliest_start_time=earliest_start_time,
            robot_id=robot_id,
        )

        return update_serial_order_request
