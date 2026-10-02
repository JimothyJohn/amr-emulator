from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeepLaneSetting1")


@_attrs_define
class DeepLaneSetting1:
    """
    Attributes:
        pallet_length (float | Unset):
        pallet_width (float | Unset):
        pallet_amount (int | Unset):
    """

    pallet_length: float | Unset = UNSET
    pallet_width: float | Unset = UNSET
    pallet_amount: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        pallet_length = self.pallet_length

        pallet_width = self.pallet_width

        pallet_amount = self.pallet_amount

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if pallet_length is not UNSET:
            field_dict["pallet-length"] = pallet_length
        if pallet_width is not UNSET:
            field_dict["pallet-width"] = pallet_width
        if pallet_amount is not UNSET:
            field_dict["pallet-amount"] = pallet_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pallet_length = d.pop("pallet-length", UNSET)

        pallet_width = d.pop("pallet-width", UNSET)

        pallet_amount = d.pop("pallet-amount", UNSET)

        deep_lane_setting_1 = cls(
            pallet_length=pallet_length,
            pallet_width=pallet_width,
            pallet_amount=pallet_amount,
        )

        return deep_lane_setting_1
