from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Bar1")


@_attrs_define
class Bar1:
    """
    Attributes:
        length (float | Unset):
        distance (float | Unset):
    """

    length: float | Unset = UNSET
    distance: float | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        length = self.length

        distance = self.distance

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if length is not UNSET:
            field_dict["length"] = length
        if distance is not UNSET:
            field_dict["distance"] = distance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        length = d.pop("length", UNSET)

        distance = d.pop("distance", UNSET)

        bar_1 = cls(
            length=length,
            distance=distance,
        )

        return bar_1
