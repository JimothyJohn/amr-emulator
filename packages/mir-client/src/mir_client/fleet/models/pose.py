from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Pose")


@_attrs_define
class Pose:
    """
    Attributes:
        x (float):
        y (float):
        orientation (float):
    """

    x: float
    y: float
    orientation: float

    def to_dict(self) -> dict[str, Any]:
        x = self.x

        y = self.y

        orientation = self.orientation

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "x": x,
                "y": y,
                "orientation": orientation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        x = d.pop("x")

        y = d.pop("y")

        orientation = d.pop("orientation")

        pose = cls(
            x=x,
            y=y,
            orientation=orientation,
        )

        return pose
