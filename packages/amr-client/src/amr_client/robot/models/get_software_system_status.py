from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSoftwareSystemStatus")


@_attrs_define
class GetSoftwareSystemStatus:
    """
    Attributes:
        application_version (str | Unset): Mir_application sw version
        free_disk_space (str | Unset): Free disk space in the sw images partition
        last_sw_update_date (datetime.datetime | Unset): The date of the last upgrade in the system
        last_sw_update_status (str | Unset): Status of the last upgrade in the system
        last_sw_update_type (str | Unset): Status of the last upgrade in the system
        platform_version (str | Unset): Mir_platform sw version
        url (str | Unset): The URL of the resource
        used_disk_space (str | Unset): Used disk space in the sw images partition
    """

    application_version: str | Unset = UNSET
    free_disk_space: str | Unset = UNSET
    last_sw_update_date: datetime.datetime | Unset = UNSET
    last_sw_update_status: str | Unset = UNSET
    last_sw_update_type: str | Unset = UNSET
    platform_version: str | Unset = UNSET
    url: str | Unset = UNSET
    used_disk_space: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        application_version = self.application_version

        free_disk_space = self.free_disk_space

        last_sw_update_date: str | Unset = UNSET
        if not isinstance(self.last_sw_update_date, Unset):
            last_sw_update_date = self.last_sw_update_date.isoformat()

        last_sw_update_status = self.last_sw_update_status

        last_sw_update_type = self.last_sw_update_type

        platform_version = self.platform_version

        url = self.url

        used_disk_space = self.used_disk_space

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if application_version is not UNSET:
            field_dict["application_version"] = application_version
        if free_disk_space is not UNSET:
            field_dict["free_disk_space"] = free_disk_space
        if last_sw_update_date is not UNSET:
            field_dict["last_sw_update_date"] = last_sw_update_date
        if last_sw_update_status is not UNSET:
            field_dict["last_sw_update_status"] = last_sw_update_status
        if last_sw_update_type is not UNSET:
            field_dict["last_sw_update_type"] = last_sw_update_type
        if platform_version is not UNSET:
            field_dict["platform_version"] = platform_version
        if url is not UNSET:
            field_dict["url"] = url
        if used_disk_space is not UNSET:
            field_dict["used_disk_space"] = used_disk_space

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        application_version = d.pop("application_version", UNSET)

        free_disk_space = d.pop("free_disk_space", UNSET)

        _last_sw_update_date = d.pop("last_sw_update_date", UNSET)
        last_sw_update_date: datetime.datetime | Unset
        if isinstance(_last_sw_update_date, Unset):
            last_sw_update_date = UNSET
        else:
            last_sw_update_date = datetime.datetime.fromisoformat(_last_sw_update_date)

        last_sw_update_status = d.pop("last_sw_update_status", UNSET)

        last_sw_update_type = d.pop("last_sw_update_type", UNSET)

        platform_version = d.pop("platform_version", UNSET)

        url = d.pop("url", UNSET)

        used_disk_space = d.pop("used_disk_space", UNSET)

        get_software_system_status = cls(
            application_version=application_version,
            free_disk_space=free_disk_space,
            last_sw_update_date=last_sw_update_date,
            last_sw_update_status=last_sw_update_status,
            last_sw_update_type=last_sw_update_type,
            platform_version=platform_version,
            url=url,
            used_disk_space=used_disk_space,
        )

        get_software_system_status.additional_properties = d
        return get_software_system_status

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
