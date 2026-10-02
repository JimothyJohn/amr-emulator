from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.directional_zone_direction import DirectionalZoneDirection
from ..types import UNSET, Unset

T = TypeVar("T", bound="DirectionalZone")


@_attrs_define
class DirectionalZone:
    """
    Attributes:
        direction (DirectionalZoneDirection | Unset):
    """

    direction: DirectionalZoneDirection | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        direction: str | Unset = UNSET
        if not isinstance(self.direction, Unset):
            direction = self.direction.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if direction is not UNSET:
            field_dict["direction"] = direction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _direction = d.pop("direction", UNSET)
        direction: DirectionalZoneDirection | Unset
        if isinstance(_direction, Unset):
            direction = UNSET
        else:
            direction = DirectionalZoneDirection(_direction)

        directional_zone = cls(
            direction=direction,
        )

        return directional_zone
