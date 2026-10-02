from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSettingGroupSettings")


@_attrs_define
class GetSettingGroupSettings:
    """
    Attributes:
        default (str | Unset):
        id (int | Unset):
        name (str | Unset):
        parent_name (str | Unset):
        url (str | Unset): The URL of the resource
        value (str | Unset):
    """

    default: str | Unset = UNSET
    id: int | Unset = UNSET
    name: str | Unset = UNSET
    parent_name: str | Unset = UNSET
    url: str | Unset = UNSET
    value: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        default = self.default

        id = self.id

        name = self.name

        parent_name = self.parent_name

        url = self.url

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default is not UNSET:
            field_dict["default"] = default
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if parent_name is not UNSET:
            field_dict["parent_name"] = parent_name
        if url is not UNSET:
            field_dict["url"] = url
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        default = d.pop("default", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        parent_name = d.pop("parent_name", UNSET)

        url = d.pop("url", UNSET)

        value = d.pop("value", UNSET)

        get_setting_group_settings = cls(
            default=default,
            id=id,
            name=name,
            parent_name=parent_name,
            url=url,
            value=value,
        )

        get_setting_group_settings.additional_properties = d
        return get_setting_group_settings

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
