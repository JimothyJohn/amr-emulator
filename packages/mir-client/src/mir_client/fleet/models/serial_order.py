from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..models.serial_order_priority import SerialOrderPriority
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.phase import Phase


T = TypeVar("T", bound="SerialOrder")


@_attrs_define
class SerialOrder:
    """
    Attributes:
        phases (list[Phase]):
        id (None | str | Unset):
        priority (SerialOrderPriority | Unset):
        earliest_start_time (datetime.datetime | None | Unset):
        robot_id (None | Unset | UUID):
    """

    phases: list[Phase]
    id: None | str | Unset = UNSET
    priority: SerialOrderPriority | Unset = UNSET
    earliest_start_time: datetime.datetime | None | Unset = UNSET
    robot_id: None | Unset | UUID = UNSET

    def to_dict(self) -> dict[str, Any]:
        phases = []
        for phases_item_data in self.phases:
            phases_item = phases_item_data.to_dict()
            phases.append(phases_item)

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

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
                "phases": phases,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if priority is not UNSET:
            field_dict["priority"] = priority
        if earliest_start_time is not UNSET:
            field_dict["earliest-start-time"] = earliest_start_time
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.phase import Phase

        d = dict(src_dict)
        phases = []
        _phases = d.pop("phases")
        for phases_item_data in _phases:
            phases_item = Phase.from_dict(phases_item_data)

            phases.append(phases_item)

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

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

        serial_order = cls(
            phases=phases,
            id=id,
            priority=priority,
            earliest_start_time=earliest_start_time,
            robot_id=robot_id,
        )

        return serial_order
