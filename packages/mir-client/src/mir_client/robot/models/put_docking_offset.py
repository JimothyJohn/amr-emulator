from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutDockingOffset")


@_attrs_define
class PutDockingOffset:
    """
    Attributes:
        name (str | Unset): Min length: 1, Max length: 255
        orientation_offset (float | Unset):
        x_offset (float | Unset):
        y_offset (float | Unset):
    """

    name: str | Unset = UNSET
    orientation_offset: float | Unset = UNSET
    x_offset: float | Unset = UNSET
    y_offset: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        orientation_offset = self.orientation_offset

        x_offset = self.x_offset

        y_offset = self.y_offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if orientation_offset is not UNSET:
            field_dict["orientation_offset"] = orientation_offset
        if x_offset is not UNSET:
            field_dict["x_offset"] = x_offset
        if y_offset is not UNSET:
            field_dict["y_offset"] = y_offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        orientation_offset = d.pop("orientation_offset", UNSET)

        x_offset = d.pop("x_offset", UNSET)

        y_offset = d.pop("y_offset", UNSET)

        put_docking_offset = cls(
            name=name,
            orientation_offset=orientation_offset,
            x_offset=x_offset,
            y_offset=y_offset,
        )

        put_docking_offset.additional_properties = d
        return put_docking_offset

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
