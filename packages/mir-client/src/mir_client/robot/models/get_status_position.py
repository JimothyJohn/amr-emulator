from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetStatusPosition")


@_attrs_define
class GetStatusPosition:
    """
    Attributes:
        orientation (float | Unset): The orientation of the current position of the robot
        x (float | Unset): The x-coordinate of the current position of the robot
        y (float | Unset): The y-coordinate of the current position of the robot
    """

    orientation: float | Unset = UNSET
    x: float | Unset = UNSET
    y: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        orientation = self.orientation

        x = self.x

        y = self.y

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if orientation is not UNSET:
            field_dict["orientation"] = orientation
        if x is not UNSET:
            field_dict["x"] = x
        if y is not UNSET:
            field_dict["y"] = y

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        orientation = d.pop("orientation", UNSET)

        x = d.pop("x", UNSET)

        y = d.pop("y", UNSET)

        get_status_position = cls(
            orientation=orientation,
            x=x,
            y=y,
        )

        get_status_position.additional_properties = d
        return get_status_position

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
