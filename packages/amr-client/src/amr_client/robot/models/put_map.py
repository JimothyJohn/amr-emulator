from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutMap")


@_attrs_define
class PutMap:
    """
    Attributes:
        base_map (str | Unset):
        name (str | Unset): Min length: 1, Max length: 40
        origin_theta (float | Unset):
        origin_x (float | Unset):
        origin_y (float | Unset):
        resolution (float | Unset): Deprecated
    """

    base_map: str | Unset = UNSET
    name: str | Unset = UNSET
    origin_theta: float | Unset = UNSET
    origin_x: float | Unset = UNSET
    origin_y: float | Unset = UNSET
    resolution: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_map = self.base_map

        name = self.name

        origin_theta = self.origin_theta

        origin_x = self.origin_x

        origin_y = self.origin_y

        resolution = self.resolution

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if base_map is not UNSET:
            field_dict["base_map"] = base_map
        if name is not UNSET:
            field_dict["name"] = name
        if origin_theta is not UNSET:
            field_dict["origin_theta"] = origin_theta
        if origin_x is not UNSET:
            field_dict["origin_x"] = origin_x
        if origin_y is not UNSET:
            field_dict["origin_y"] = origin_y
        if resolution is not UNSET:
            field_dict["resolution"] = resolution

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        base_map = d.pop("base_map", UNSET)

        name = d.pop("name", UNSET)

        origin_theta = d.pop("origin_theta", UNSET)

        origin_x = d.pop("origin_x", UNSET)

        origin_y = d.pop("origin_y", UNSET)

        resolution = d.pop("resolution", UNSET)

        put_map = cls(
            base_map=base_map,
            name=name,
            origin_theta=origin_theta,
            origin_x=origin_x,
            origin_y=origin_y,
            resolution=resolution,
        )

        put_map.additional_properties = d
        return put_map

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
