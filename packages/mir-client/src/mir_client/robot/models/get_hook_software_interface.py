from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetHookSoftwareInterface")


@_attrs_define
class GetHookSoftwareInterface:
    """
    Attributes:
        hook_interface_state (str | Unset): Hook interface state
        hook_interface_state_code (int | Unset): Hook interface state
        hook_is_upgradeable (bool | Unset): Wheater the hook is ready to be upgraded
        hook_is_upgrading (bool | Unset): Wheater the hook is upgrading now
        hook_software_matches_robot (bool | Unset): Wheter the hook software version matches the robot version
        hook_software_newer_than_robot (bool | Unset): Whether hook software version is newer than robot version
        hook_software_version (str | Unset): Hook software version
        software_file_missing (bool | Unset): Original software file not found.
        uploading_software_to_hook (bool | Unset): Wheater we are currently uploading software to hook
    """

    hook_interface_state: str | Unset = UNSET
    hook_interface_state_code: int | Unset = UNSET
    hook_is_upgradeable: bool | Unset = UNSET
    hook_is_upgrading: bool | Unset = UNSET
    hook_software_matches_robot: bool | Unset = UNSET
    hook_software_newer_than_robot: bool | Unset = UNSET
    hook_software_version: str | Unset = UNSET
    software_file_missing: bool | Unset = UNSET
    uploading_software_to_hook: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hook_interface_state = self.hook_interface_state

        hook_interface_state_code = self.hook_interface_state_code

        hook_is_upgradeable = self.hook_is_upgradeable

        hook_is_upgrading = self.hook_is_upgrading

        hook_software_matches_robot = self.hook_software_matches_robot

        hook_software_newer_than_robot = self.hook_software_newer_than_robot

        hook_software_version = self.hook_software_version

        software_file_missing = self.software_file_missing

        uploading_software_to_hook = self.uploading_software_to_hook

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hook_interface_state is not UNSET:
            field_dict["hook_interface_state"] = hook_interface_state
        if hook_interface_state_code is not UNSET:
            field_dict["hook_interface_state_code"] = hook_interface_state_code
        if hook_is_upgradeable is not UNSET:
            field_dict["hook_is_upgradeable"] = hook_is_upgradeable
        if hook_is_upgrading is not UNSET:
            field_dict["hook_is_upgrading"] = hook_is_upgrading
        if hook_software_matches_robot is not UNSET:
            field_dict["hook_software_matches_robot"] = hook_software_matches_robot
        if hook_software_newer_than_robot is not UNSET:
            field_dict["hook_software_newer_than_robot"] = hook_software_newer_than_robot
        if hook_software_version is not UNSET:
            field_dict["hook_software_version"] = hook_software_version
        if software_file_missing is not UNSET:
            field_dict["software_file_missing"] = software_file_missing
        if uploading_software_to_hook is not UNSET:
            field_dict["uploading_software_to_hook"] = uploading_software_to_hook

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hook_interface_state = d.pop("hook_interface_state", UNSET)

        hook_interface_state_code = d.pop("hook_interface_state_code", UNSET)

        hook_is_upgradeable = d.pop("hook_is_upgradeable", UNSET)

        hook_is_upgrading = d.pop("hook_is_upgrading", UNSET)

        hook_software_matches_robot = d.pop("hook_software_matches_robot", UNSET)

        hook_software_newer_than_robot = d.pop("hook_software_newer_than_robot", UNSET)

        hook_software_version = d.pop("hook_software_version", UNSET)

        software_file_missing = d.pop("software_file_missing", UNSET)

        uploading_software_to_hook = d.pop("uploading_software_to_hook", UNSET)

        get_hook_software_interface = cls(
            hook_interface_state=hook_interface_state,
            hook_interface_state_code=hook_interface_state_code,
            hook_is_upgradeable=hook_is_upgradeable,
            hook_is_upgrading=hook_is_upgrading,
            hook_software_matches_robot=hook_software_matches_robot,
            hook_software_newer_than_robot=hook_software_newer_than_robot,
            hook_software_version=hook_software_version,
            software_file_missing=software_file_missing,
            uploading_software_to_hook=uploading_software_to_hook,
        )

        get_hook_software_interface.additional_properties = d
        return get_hook_software_interface

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
