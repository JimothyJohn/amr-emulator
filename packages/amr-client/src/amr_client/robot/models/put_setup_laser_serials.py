from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutSetupLaserSerials")


@_attrs_define
class PutSetupLaserSerials:
    """
    Attributes:
        back_laser_serial (str | Unset): Max length: 20
        front_laser_serial (str | Unset): Max length: 20
        operation (str | Unset): Max length: 20
    """

    back_laser_serial: str | Unset = UNSET
    front_laser_serial: str | Unset = UNSET
    operation: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        back_laser_serial = self.back_laser_serial

        front_laser_serial = self.front_laser_serial

        operation = self.operation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if back_laser_serial is not UNSET:
            field_dict["back_laser_serial"] = back_laser_serial
        if front_laser_serial is not UNSET:
            field_dict["front_laser_serial"] = front_laser_serial
        if operation is not UNSET:
            field_dict["operation"] = operation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        back_laser_serial = d.pop("back_laser_serial", UNSET)

        front_laser_serial = d.pop("front_laser_serial", UNSET)

        operation = d.pop("operation", UNSET)

        put_setup_laser_serials = cls(
            back_laser_serial=back_laser_serial,
            front_laser_serial=front_laser_serial,
            operation=operation,
        )

        put_setup_laser_serials.additional_properties = d
        return put_setup_laser_serials

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
