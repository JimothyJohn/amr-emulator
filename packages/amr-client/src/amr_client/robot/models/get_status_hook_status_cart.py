from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetStatusHookStatusCart")


@_attrs_define
class GetStatusHookStatusCart:
    """
    Attributes:
        height (float | Unset): The height of the attached trolley
        id (float | Unset): The id of the attached trolley
        length (float | Unset): The length of the attached trolley
        offset_locked_wheels (float | Unset): The distance from front of the attached trolley to the locked wheels
        width (float | Unset): The width of the attached trolley
    """

    height: float | Unset = UNSET
    id: float | Unset = UNSET
    length: float | Unset = UNSET
    offset_locked_wheels: float | Unset = UNSET
    width: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        height = self.height

        id = self.id

        length = self.length

        offset_locked_wheels = self.offset_locked_wheels

        width = self.width

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if height is not UNSET:
            field_dict["height"] = height
        if id is not UNSET:
            field_dict["id"] = id
        if length is not UNSET:
            field_dict["length"] = length
        if offset_locked_wheels is not UNSET:
            field_dict["offset_locked_wheels"] = offset_locked_wheels
        if width is not UNSET:
            field_dict["width"] = width

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        height = d.pop("height", UNSET)

        id = d.pop("id", UNSET)

        length = d.pop("length", UNSET)

        offset_locked_wheels = d.pop("offset_locked_wheels", UNSET)

        width = d.pop("width", UNSET)

        get_status_hook_status_cart = cls(
            height=height,
            id=id,
            length=length,
            offset_locked_wheels=offset_locked_wheels,
            width=width,
        )

        get_status_hook_status_cart.additional_properties = d
        return get_status_hook_status_cart

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
