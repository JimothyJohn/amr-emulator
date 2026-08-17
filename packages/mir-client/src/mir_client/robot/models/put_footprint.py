from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutFootprint")


@_attrs_define
class PutFootprint:
    """
    Attributes:
        config_id (str | Unset): Choices are: {"MIR500-1000", "MIR600-1350", "MIR100-200", "MIR250", "UNKNOWN"}
        footprint_points (str | Unset):
        height (float | Unset):
        hook (bool | Unset):
        name (str | Unset): Min length: 1, Max length: 255
    """

    config_id: str | Unset = UNSET
    footprint_points: str | Unset = UNSET
    height: float | Unset = UNSET
    hook: bool | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config_id = self.config_id

        footprint_points = self.footprint_points

        height = self.height

        hook = self.hook

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config_id is not UNSET:
            field_dict["config_id"] = config_id
        if footprint_points is not UNSET:
            field_dict["footprint_points"] = footprint_points
        if height is not UNSET:
            field_dict["height"] = height
        if hook is not UNSET:
            field_dict["hook"] = hook
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        config_id = d.pop("config_id", UNSET)

        footprint_points = d.pop("footprint_points", UNSET)

        height = d.pop("height", UNSET)

        hook = d.pop("hook", UNSET)

        name = d.pop("name", UNSET)

        put_footprint = cls(
            config_id=config_id,
            footprint_points=footprint_points,
            height=height,
            hook=hook,
            name=name,
        )

        put_footprint.additional_properties = d
        return put_footprint

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
