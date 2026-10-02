from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSoftwareRobotPeripheralsStatus")


@_attrs_define
class GetSoftwareRobotPeripheralsStatus:
    """
    Attributes:
        current_upgrade_status (str | Unset): Current peripheral upgrade status
        current_upgrade_status_msg (str | Unset): Current peripheral upgrade status message
        current_version (str | Unset): Current peripheral fw/sw version
        peripheral_name (str | Unset): Peripheral name
        upgrade_succeeded (str | Unset): True if upgrade is successful, false if failed, if in progress, it should be a
            string with progress
        url (str | Unset): The URL of the resource
    """

    current_upgrade_status: str | Unset = UNSET
    current_upgrade_status_msg: str | Unset = UNSET
    current_version: str | Unset = UNSET
    peripheral_name: str | Unset = UNSET
    upgrade_succeeded: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        current_upgrade_status = self.current_upgrade_status

        current_upgrade_status_msg = self.current_upgrade_status_msg

        current_version = self.current_version

        peripheral_name = self.peripheral_name

        upgrade_succeeded = self.upgrade_succeeded

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if current_upgrade_status is not UNSET:
            field_dict["current_upgrade_status"] = current_upgrade_status
        if current_upgrade_status_msg is not UNSET:
            field_dict["current_upgrade_status_msg"] = current_upgrade_status_msg
        if current_version is not UNSET:
            field_dict["current_version"] = current_version
        if peripheral_name is not UNSET:
            field_dict["peripheral_name"] = peripheral_name
        if upgrade_succeeded is not UNSET:
            field_dict["upgrade_succeeded"] = upgrade_succeeded
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_upgrade_status = d.pop("current_upgrade_status", UNSET)

        current_upgrade_status_msg = d.pop("current_upgrade_status_msg", UNSET)

        current_version = d.pop("current_version", UNSET)

        peripheral_name = d.pop("peripheral_name", UNSET)

        upgrade_succeeded = d.pop("upgrade_succeeded", UNSET)

        url = d.pop("url", UNSET)

        get_software_robot_peripherals_status = cls(
            current_upgrade_status=current_upgrade_status,
            current_upgrade_status_msg=current_upgrade_status_msg,
            current_version=current_version,
            peripheral_name=peripheral_name,
            upgrade_succeeded=upgrade_succeeded,
            url=url,
        )

        get_software_robot_peripherals_status.additional_properties = d
        return get_software_robot_peripherals_status

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
