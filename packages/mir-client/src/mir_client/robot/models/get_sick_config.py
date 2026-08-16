from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_sick_config_supported_software_version import (
        GetSickConfigSupportedSoftwareVersion,
    )


T = TypeVar("T", bound="GetSickConfig")


@_attrs_define
class GetSickConfig:
    """
    Attributes:
        crc (str | Unset):
        description (str | Unset):
        filename (str | Unset):
        guid (str | Unset):
        supported_software_version (GetSickConfigSupportedSoftwareVersion | Unset):
        url (str | Unset): Specific sick configuration file.
    """

    crc: str | Unset = UNSET
    description: str | Unset = UNSET
    filename: str | Unset = UNSET
    guid: str | Unset = UNSET
    supported_software_version: GetSickConfigSupportedSoftwareVersion | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        crc = self.crc

        description = self.description

        filename = self.filename

        guid = self.guid

        supported_software_version: dict[str, Any] | Unset = UNSET
        if not isinstance(self.supported_software_version, Unset):
            supported_software_version = self.supported_software_version.to_dict()

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if crc is not UNSET:
            field_dict["crc"] = crc
        if description is not UNSET:
            field_dict["description"] = description
        if filename is not UNSET:
            field_dict["filename"] = filename
        if guid is not UNSET:
            field_dict["guid"] = guid
        if supported_software_version is not UNSET:
            field_dict["supported_software_version"] = supported_software_version
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_sick_config_supported_software_version import (
            GetSickConfigSupportedSoftwareVersion,
        )

        d = dict(src_dict)
        crc = d.pop("crc", UNSET)

        description = d.pop("description", UNSET)

        filename = d.pop("filename", UNSET)

        guid = d.pop("guid", UNSET)

        _supported_software_version = d.pop("supported_software_version", UNSET)
        supported_software_version: GetSickConfigSupportedSoftwareVersion | Unset
        if isinstance(_supported_software_version, Unset):
            supported_software_version = UNSET
        else:
            supported_software_version = GetSickConfigSupportedSoftwareVersion.from_dict(
                _supported_software_version
            )

        url = d.pop("url", UNSET)

        get_sick_config = cls(
            crc=crc,
            description=description,
            filename=filename,
            guid=guid,
            supported_software_version=supported_software_version,
            url=url,
        )

        get_sick_config.additional_properties = d
        return get_sick_config

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
