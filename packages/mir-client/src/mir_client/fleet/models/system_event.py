from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evacuation import Evacuation
    from ..models.robot import Robot


T = TypeVar("T", bound="SystemEvent")


@_attrs_define
class SystemEvent:
    """
    Attributes:
        evacuation (Evacuation | Unset):
        robot (Robot | Unset):
        timestamp (datetime.datetime | Unset):
    """

    evacuation: Evacuation | Unset = UNSET
    robot: Robot | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        evacuation: dict[str, Any] | Unset = UNSET
        if not isinstance(self.evacuation, Unset):
            evacuation = self.evacuation.to_dict()

        robot: dict[str, Any] | Unset = UNSET
        if not isinstance(self.robot, Unset):
            robot = self.robot.to_dict()

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if evacuation is not UNSET:
            field_dict["evacuation"] = evacuation
        if robot is not UNSET:
            field_dict["robot"] = robot
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evacuation import Evacuation
        from ..models.robot import Robot

        d = dict(src_dict)
        _evacuation = d.pop("evacuation", UNSET)
        evacuation: Evacuation | Unset
        if isinstance(_evacuation, Unset):
            evacuation = UNSET
        else:
            evacuation = Evacuation.from_dict(_evacuation)

        _robot = d.pop("robot", UNSET)
        robot: Robot | Unset
        if isinstance(_robot, Unset):
            robot = UNSET
        else:
            robot = Robot.from_dict(_robot)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        system_event = cls(
            evacuation=evacuation,
            robot=robot,
            timestamp=timestamp,
        )

        return system_event
