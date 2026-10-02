from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetCarts")


@_attrs_define
class GetCarts:
    """
    Attributes:
        cart_calibration (str | Unset): The url to the calibration of this cart
        cart_type (str | Unset): The url to the type of this cart
        guid (str | Unset): The global id unique across robots that identifies this cart
        name (str | Unset): The name of the cart
        url (str | Unset): The URL of the resource
    """

    cart_calibration: str | Unset = UNSET
    cart_type: str | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cart_calibration = self.cart_calibration

        cart_type = self.cart_type

        guid = self.guid

        name = self.name

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cart_calibration is not UNSET:
            field_dict["cart_calibration"] = cart_calibration
        if cart_type is not UNSET:
            field_dict["cart_type"] = cart_type
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cart_calibration = d.pop("cart_calibration", UNSET)

        cart_type = d.pop("cart_type", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        get_carts = cls(
            cart_calibration=cart_calibration,
            cart_type=cart_type,
            guid=guid,
            name=name,
            url=url,
        )

        get_carts.additional_properties = d
        return get_carts

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
