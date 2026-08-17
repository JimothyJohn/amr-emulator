from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Elevation")


@_attrs_define
class Elevation:
    """
    Attributes:
        height (float):
        relative_lift_distance (float):
    """

    height: float
    relative_lift_distance: float

    def to_dict(self) -> dict[str, Any]:
        height = self.height

        relative_lift_distance = self.relative_lift_distance

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "height": height,
                "relative-lift-distance": relative_lift_distance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        height = d.pop("height")

        relative_lift_distance = d.pop("relative-lift-distance")

        elevation = cls(
            height=height,
            relative_lift_distance=relative_lift_distance,
        )

        return elevation
