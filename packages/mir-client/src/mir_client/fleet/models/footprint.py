from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.point import Point


T = TypeVar("T", bound="Footprint")


@_attrs_define
class Footprint:
    """
    Attributes:
        points (list[Point]):
        height (float):
    """

    points: list[Point]
    height: float

    def to_dict(self) -> dict[str, Any]:
        points = []
        for points_item_data in self.points:
            points_item = points_item_data.to_dict()
            points.append(points_item)

        height = self.height

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "points": points,
                "height": height,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.point import Point

        d = dict(src_dict)
        points = []
        _points = d.pop("points")
        for points_item_data in _points:
            points_item = Point.from_dict(points_item_data)

            points.append(points_item)

        height = d.pop("height")

        footprint = cls(
            points=points,
            height=height,
        )

        return footprint
