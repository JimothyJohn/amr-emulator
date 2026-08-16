from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="DeepLaneSetting")


@_attrs_define
class DeepLaneSetting:
    """
    Attributes:
        pallet_length (float):
        pallet_width (float):
        pallet_amount (int):
    """

    pallet_length: float
    pallet_width: float
    pallet_amount: int

    def to_dict(self) -> dict[str, Any]:
        pallet_length = self.pallet_length

        pallet_width = self.pallet_width

        pallet_amount = self.pallet_amount

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "pallet-length": pallet_length,
                "pallet-width": pallet_width,
                "pallet-amount": pallet_amount,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pallet_length = d.pop("pallet-length")

        pallet_width = d.pop("pallet-width")

        pallet_amount = d.pop("pallet-amount")

        deep_lane_setting = cls(
            pallet_length=pallet_length,
            pallet_width=pallet_width,
            pallet_amount=pallet_amount,
        )

        return deep_lane_setting
