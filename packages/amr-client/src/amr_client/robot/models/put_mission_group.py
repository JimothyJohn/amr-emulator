from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutMissionGroup")


@_attrs_define
class PutMissionGroup:
    """
    Attributes:
        feature (str | Unset): Min length: 1, Max length: 63
        icon (str | Unset):
        name (str | Unset): Min length: 1, Max length: 63
        priority (int | Unset):
    """

    feature: str | Unset = UNSET
    icon: str | Unset = UNSET
    name: str | Unset = UNSET
    priority: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        feature = self.feature

        icon = self.icon

        name = self.name

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if feature is not UNSET:
            field_dict["feature"] = feature
        if icon is not UNSET:
            field_dict["icon"] = icon
        if name is not UNSET:
            field_dict["name"] = name
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        feature = d.pop("feature", UNSET)

        icon = d.pop("icon", UNSET)

        name = d.pop("name", UNSET)

        priority = d.pop("priority", UNSET)

        put_mission_group = cls(
            feature=feature,
            icon=icon,
            name=name,
            priority=priority,
        )

        put_mission_group.additional_properties = d
        return put_mission_group

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
