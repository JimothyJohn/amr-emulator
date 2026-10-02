from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Elevation1")


@_attrs_define
class Elevation1:
    """
    Attributes:
        height (float | Unset):
        relative_lift_distance (float | Unset):
    """

    height: float | Unset = UNSET
    relative_lift_distance: float | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        height = self.height

        relative_lift_distance = self.relative_lift_distance

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if height is not UNSET:
            field_dict["height"] = height
        if relative_lift_distance is not UNSET:
            field_dict["relative-lift-distance"] = relative_lift_distance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        height = d.pop("height", UNSET)

        relative_lift_distance = d.pop("relative-lift-distance", UNSET)

        elevation_1 = cls(
            height=height,
            relative_lift_distance=relative_lift_distance,
        )

        return elevation_1
