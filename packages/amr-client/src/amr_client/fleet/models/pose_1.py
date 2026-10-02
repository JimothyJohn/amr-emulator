from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Pose1")


@_attrs_define
class Pose1:
    """
    Attributes:
        x (float | Unset):
        y (float | Unset):
        orientation (float | Unset):
    """

    x: float | Unset = UNSET
    y: float | Unset = UNSET
    orientation: float | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        x = self.x

        y = self.y

        orientation = self.orientation

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if x is not UNSET:
            field_dict["x"] = x
        if y is not UNSET:
            field_dict["y"] = y
        if orientation is not UNSET:
            field_dict["orientation"] = orientation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        x = d.pop("x", UNSET)

        y = d.pop("y", UNSET)

        orientation = d.pop("orientation", UNSET)

        pose_1 = cls(
            x=x,
            y=y,
            orientation=orientation,
        )

        return pose_1
