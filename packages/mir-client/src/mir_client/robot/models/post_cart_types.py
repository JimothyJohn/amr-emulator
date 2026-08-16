from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostCartTypes")


@_attrs_define
class PostCartTypes:
    """
    Attributes:
        height (float):
        length (float):
        name (str): Min length: 1, Max length: 40
        offset_locked_wheels (float):
        width (float):
        created_by_id (str | Unset):
        guid (str | Unset):
    """

    height: float
    length: float
    name: str
    offset_locked_wheels: float
    width: float
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        height = self.height

        length = self.length

        name = self.name

        offset_locked_wheels = self.offset_locked_wheels

        width = self.width

        created_by_id = self.created_by_id

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "height": height,
                "length": length,
                "name": name,
                "offset_locked_wheels": offset_locked_wheels,
                "width": width,
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
        height = d.pop("height")

        length = d.pop("length")

        name = d.pop("name")

        offset_locked_wheels = d.pop("offset_locked_wheels")

        width = d.pop("width")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        post_cart_types = cls(
            height=height,
            length=length,
            name=name,
            offset_locked_wheels=offset_locked_wheels,
            width=width,
            created_by_id=created_by_id,
            guid=guid,
        )

        post_cart_types.additional_properties = d
        return post_cart_types

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
