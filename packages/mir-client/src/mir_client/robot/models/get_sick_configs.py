from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSickConfigs")


@_attrs_define
class GetSickConfigs:
    """
    Attributes:
        description (str | Unset):
        filename (str | Unset):
        guid (str | Unset):
        url (str | Unset): The URL of the resource
    """

    description: str | Unset = UNSET
    filename: str | Unset = UNSET
    guid: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        filename = self.filename

        guid = self.guid

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if filename is not UNSET:
            field_dict["filename"] = filename
        if guid is not UNSET:
            field_dict["guid"] = guid
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        filename = d.pop("filename", UNSET)

        guid = d.pop("guid", UNSET)

        url = d.pop("url", UNSET)

        get_sick_configs = cls(
            description=description,
            filename=filename,
            guid=guid,
            url=url,
        )

        get_sick_configs.additional_properties = d
        return get_sick_configs

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
