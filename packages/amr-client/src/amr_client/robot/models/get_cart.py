from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetCart")


@_attrs_define
class GetCart:
    """
    Attributes:
        cart_calibration (str | Unset): The url to the calibration of this cart
        cart_calibration_id (str | Unset): The id of the calibration for this cart has
        cart_type (str | Unset): The url to the type of this cart
        cart_type_id (str | Unset): The id of the type of this cart
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global id unique across robots that identifies this cart
        name (str | Unset): The name of the cart
    """

    cart_calibration: str | Unset = UNSET
    cart_calibration_id: str | Unset = UNSET
    cart_type: str | Unset = UNSET
    cart_type_id: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cart_calibration = self.cart_calibration

        cart_calibration_id = self.cart_calibration_id

        cart_type = self.cart_type

        cart_type_id = self.cart_type_id

        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cart_calibration is not UNSET:
            field_dict["cart_calibration"] = cart_calibration
        if cart_calibration_id is not UNSET:
            field_dict["cart_calibration_id"] = cart_calibration_id
        if cart_type is not UNSET:
            field_dict["cart_type"] = cart_type
        if cart_type_id is not UNSET:
            field_dict["cart_type_id"] = cart_type_id
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cart_calibration = d.pop("cart_calibration", UNSET)

        cart_calibration_id = d.pop("cart_calibration_id", UNSET)

        cart_type = d.pop("cart_type", UNSET)

        cart_type_id = d.pop("cart_type_id", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        get_cart = cls(
            cart_calibration=cart_calibration,
            cart_calibration_id=cart_calibration_id,
            cart_type=cart_type,
            cart_type_id=cart_type_id,
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            name=name,
        )

        get_cart.additional_properties = d
        return get_cart

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
