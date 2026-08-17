from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSoftwareUpgrades")


@_attrs_define
class GetSoftwareUpgrades:
    """
    Attributes:
        guid (str | Unset): The guid of the software upgrade
        type_ (str | Unset): The type of the software upgrade
        upload_date (datetime.datetime | Unset): The upload date of the software upgrade
        url (str | Unset): The URL of the resource
        version (str | Unset): The version of the software upgrade
    """

    guid: str | Unset = UNSET
    type_: str | Unset = UNSET
    upload_date: datetime.datetime | Unset = UNSET
    url: str | Unset = UNSET
    version: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        type_ = self.type_

        upload_date: str | Unset = UNSET
        if not isinstance(self.upload_date, Unset):
            upload_date = self.upload_date.isoformat()

        url = self.url

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if type_ is not UNSET:
            field_dict["type"] = type_
        if upload_date is not UNSET:
            field_dict["upload_date"] = upload_date
        if url is not UNSET:
            field_dict["url"] = url
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        type_ = d.pop("type", UNSET)

        _upload_date = d.pop("upload_date", UNSET)
        upload_date: datetime.datetime | Unset
        if isinstance(_upload_date, Unset):
            upload_date = UNSET
        else:
            upload_date = datetime.datetime.fromisoformat(_upload_date)

        url = d.pop("url", UNSET)

        version = d.pop("version", UNSET)

        get_software_upgrades = cls(
            guid=guid,
            type_=type_,
            upload_date=upload_date,
            url=url,
            version=version,
        )

        get_software_upgrades.additional_properties = d
        return get_software_upgrades

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
