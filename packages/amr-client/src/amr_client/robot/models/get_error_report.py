from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetErrorReport")


@_attrs_define
class GetErrorReport:
    """
    Attributes:
        description (str | Unset):
        download_url (str | Unset): The url from where the bag can be downloaded
        generating (bool | Unset): Indicates whether the error log creation is running or not
        id (int | Unset): Id of the autobag
        module (str | Unset): The module that created the autolog
        ready (bool | Unset): Status of the rosbag
        time (datetime.datetime | Unset): The time where the autolog was created
    """

    description: str | Unset = UNSET
    download_url: str | Unset = UNSET
    generating: bool | Unset = UNSET
    id: int | Unset = UNSET
    module: str | Unset = UNSET
    ready: bool | Unset = UNSET
    time: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        download_url = self.download_url

        generating = self.generating

        id = self.id

        module = self.module

        ready = self.ready

        time: str | Unset = UNSET
        if not isinstance(self.time, Unset):
            time = self.time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if download_url is not UNSET:
            field_dict["download_url"] = download_url
        if generating is not UNSET:
            field_dict["generating"] = generating
        if id is not UNSET:
            field_dict["id"] = id
        if module is not UNSET:
            field_dict["module"] = module
        if ready is not UNSET:
            field_dict["ready"] = ready
        if time is not UNSET:
            field_dict["time"] = time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        download_url = d.pop("download_url", UNSET)

        generating = d.pop("generating", UNSET)

        id = d.pop("id", UNSET)

        module = d.pop("module", UNSET)

        ready = d.pop("ready", UNSET)

        _time = d.pop("time", UNSET)
        time: datetime.datetime | Unset
        if isinstance(_time, Unset):
            time = UNSET
        else:
            time = datetime.datetime.fromisoformat(_time)

        get_error_report = cls(
            description=description,
            download_url=download_url,
            generating=generating,
            id=id,
            module=module,
            ready=ready,
            time=time,
        )

        get_error_report.additional_properties = d
        return get_error_report

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
