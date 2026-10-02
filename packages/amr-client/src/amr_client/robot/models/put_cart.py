from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutCart")


@_attrs_define
class PutCart:
    """
    Attributes:
        cart_calibration_id (str | Unset):
        cart_type_id (str | Unset):
        name (str | Unset): Min length: 1, Max length: 40
    """

    cart_calibration_id: str | Unset = UNSET
    cart_type_id: str | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cart_calibration_id = self.cart_calibration_id

        cart_type_id = self.cart_type_id

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cart_calibration_id is not UNSET:
            field_dict["cart_calibration_id"] = cart_calibration_id
        if cart_type_id is not UNSET:
            field_dict["cart_type_id"] = cart_type_id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cart_calibration_id = d.pop("cart_calibration_id", UNSET)

        cart_type_id = d.pop("cart_type_id", UNSET)

        name = d.pop("name", UNSET)

        put_cart = cls(
            cart_calibration_id=cart_calibration_id,
            cart_type_id=cart_type_id,
            name=name,
        )

        put_cart.additional_properties = d
        return put_cart

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
