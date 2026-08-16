from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.robot_model import RobotModel

if TYPE_CHECKING:
    from ..models.point import Point


T = TypeVar("T", bound="Footprint1")


@_attrs_define
class Footprint1:
    """
    Attributes:
        name (str):
        robot_types (list[RobotModel]):
        has_hook (bool):
        height (float):
        points (list[Point]):
    """

    name: str
    robot_types: list[RobotModel]
    has_hook: bool
    height: float
    points: list[Point]

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        robot_types = []
        for robot_types_item_data in self.robot_types:
            robot_types_item = robot_types_item_data.value
            robot_types.append(robot_types_item)

        has_hook = self.has_hook

        height = self.height

        points = []
        for points_item_data in self.points:
            points_item = points_item_data.to_dict()
            points.append(points_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "robot-types": robot_types,
                "has-hook": has_hook,
                "height": height,
                "points": points,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.point import Point

        d = dict(src_dict)
        name = d.pop("name")

        robot_types = []
        _robot_types = d.pop("robot-types")
        for robot_types_item_data in _robot_types:
            robot_types_item = RobotModel(robot_types_item_data)

            robot_types.append(robot_types_item)

        has_hook = d.pop("has-hook")

        height = d.pop("height")

        points = []
        _points = d.pop("points")
        for points_item_data in _points:
            points_item = Point.from_dict(points_item_data)

            points.append(points_item)

        footprint_1 = cls(
            name=name,
            robot_types=robot_types,
            has_hook=has_hook,
            height=height,
            points=points,
        )

        return footprint_1
