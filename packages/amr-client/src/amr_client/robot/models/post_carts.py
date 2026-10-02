from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostCarts")


@_attrs_define
class PostCarts:
    """
    Attributes:
        cart_calibration_id (str):
        cart_type_id (str):
        name (str): Min length: 1, Max length: 40
        created_by_id (str | Unset):
        guid (str | Unset):
    """

    cart_calibration_id: str
    cart_type_id: str
    name: str
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cart_calibration_id = self.cart_calibration_id

        cart_type_id = self.cart_type_id

        name = self.name

        created_by_id = self.created_by_id

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cart_calibration_id": cart_calibration_id,
                "cart_type_id": cart_type_id,
                "name": name,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cart_calibration_id = d.pop("cart_calibration_id")

        cart_type_id = d.pop("cart_type_id")

        name = d.pop("name")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        post_carts = cls(
            cart_calibration_id=cart_calibration_id,
            cart_type_id=cart_type_id,
            name=name,
            created_by_id=created_by_id,
            guid=guid,
        )

        post_carts.additional_properties = d
        return post_carts

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
