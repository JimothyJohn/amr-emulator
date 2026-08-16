from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SpeedZone")


@_attrs_define
class SpeedZone:
    """
    Attributes:
        speed_limit (float | Unset):
    """

    speed_limit: float | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        speed_limit = self.speed_limit

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if speed_limit is not UNSET:
            field_dict["speed-limit"] = speed_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        speed_limit = d.pop("speed-limit", UNSET)

        speed_zone = cls(
            speed_limit=speed_limit,
        )

        return speed_zone
