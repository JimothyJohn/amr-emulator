from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetStatusVelocity")


@_attrs_define
class GetStatusVelocity:
    """
    Attributes:
        angular (float | Unset): The angular speed of the robot in degrees/s
        linear (float | Unset): The linear speed of the robot in m/s
    """

    angular: float | Unset = UNSET
    linear: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        angular = self.angular

        linear = self.linear

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if angular is not UNSET:
            field_dict["angular"] = angular
        if linear is not UNSET:
            field_dict["linear"] = linear

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        angular = d.pop("angular", UNSET)

        linear = d.pop("linear", UNSET)

        get_status_velocity = cls(
            angular=angular,
            linear=linear,
        )

        get_status_velocity.additional_properties = d
        return get_status_velocity

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
