from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Bar")


@_attrs_define
class Bar:
    """
    Attributes:
        length (float):
        distance (float):
    """

    length: float
    distance: float

    def to_dict(self) -> dict[str, Any]:
        length = self.length

        distance = self.distance

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "length": length,
                "distance": distance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        length = d.pop("length")

        distance = d.pop("distance")

        bar = cls(
            length=length,
            distance=distance,
        )

        return bar
