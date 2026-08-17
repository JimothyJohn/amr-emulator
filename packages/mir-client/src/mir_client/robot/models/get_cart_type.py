from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetCartType")


@_attrs_define
class GetCartType:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global id unique across robots that identifies this cart type
        height (float | Unset): The height of carts of this type
        length (float | Unset): The length of carts of this type
        name (str | Unset): The name of the cart type
        offset_locked_wheels (float | Unset): The offset from the center of the robot to the locked wheels of carts of
            this type
        width (float | Unset): The width of carts of this type
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    height: float | Unset = UNSET
    length: float | Unset = UNSET
    name: str | Unset = UNSET
    offset_locked_wheels: float | Unset = UNSET
    width: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        height = self.height

        length = self.length

        name = self.name

        offset_locked_wheels = self.offset_locked_wheels

        width = self.width

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if height is not UNSET:
            field_dict["height"] = height
        if length is not UNSET:
            field_dict["length"] = length
        if name is not UNSET:
            field_dict["name"] = name
        if offset_locked_wheels is not UNSET:
            field_dict["offset_locked_wheels"] = offset_locked_wheels
        if width is not UNSET:
            field_dict["width"] = width

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        height = d.pop("height", UNSET)

        length = d.pop("length", UNSET)

        name = d.pop("name", UNSET)

        offset_locked_wheels = d.pop("offset_locked_wheels", UNSET)

        width = d.pop("width", UNSET)

        get_cart_type = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            height=height,
            length=length,
            name=name,
            offset_locked_wheels=offset_locked_wheels,
            width=width,
        )

        get_cart_type.additional_properties = d
        return get_cart_type

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
