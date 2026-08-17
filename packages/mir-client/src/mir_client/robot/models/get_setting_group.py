from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSettingGroup")


@_attrs_define
class GetSettingGroup:
    """
    Attributes:
        advanced_settings_count (int | Unset):
        description (str | Unset):
        id (int | Unset):
        name (str | Unset):
        priority (int | Unset):
        settings_count (int | Unset):
    """

    advanced_settings_count: int | Unset = UNSET
    description: str | Unset = UNSET
    id: int | Unset = UNSET
    name: str | Unset = UNSET
    priority: int | Unset = UNSET
    settings_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        advanced_settings_count = self.advanced_settings_count

        description = self.description

        id = self.id

        name = self.name

        priority = self.priority

        settings_count = self.settings_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if advanced_settings_count is not UNSET:
            field_dict["advanced_settings_count"] = advanced_settings_count
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if priority is not UNSET:
            field_dict["priority"] = priority
        if settings_count is not UNSET:
            field_dict["settings_count"] = settings_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        advanced_settings_count = d.pop("advanced_settings_count", UNSET)

        description = d.pop("description", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        priority = d.pop("priority", UNSET)

        settings_count = d.pop("settings_count", UNSET)

        get_setting_group = cls(
            advanced_settings_count=advanced_settings_count,
            description=description,
            id=id,
            name=name,
            priority=priority,
            settings_count=settings_count,
        )

        get_setting_group.additional_properties = d
        return get_setting_group

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
