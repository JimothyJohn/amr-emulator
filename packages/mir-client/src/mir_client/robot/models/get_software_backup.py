from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSoftwareBackup")


@_attrs_define
class GetSoftwareBackup:
    """
    Attributes:
        date (datetime.datetime | Unset): The date where the backup was created
        guid (str | Unset): The guid of the software backup
        state (str | Unset): The state of the software backup
        version (str | Unset): The version of the software backup
    """

    date: datetime.datetime | Unset = UNSET
    guid: str | Unset = UNSET
    state: str | Unset = UNSET
    version: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date: str | Unset = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        guid = self.guid

        state = self.state

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date is not UNSET:
            field_dict["date"] = date
        if guid is not UNSET:
            field_dict["guid"] = guid
        if state is not UNSET:
            field_dict["state"] = state
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _date = d.pop("date", UNSET)
        date: datetime.datetime | Unset
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = datetime.datetime.fromisoformat(_date)

        guid = d.pop("guid", UNSET)

        state = d.pop("state", UNSET)

        version = d.pop("version", UNSET)

        get_software_backup = cls(
            date=date,
            guid=guid,
            state=state,
            version=version,
        )

        get_software_backup.additional_properties = d
        return get_software_backup

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
