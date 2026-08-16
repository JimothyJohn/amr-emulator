from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostMissionGroups")


@_attrs_define
class PostMissionGroups:
    """
    Attributes:
        feature (str): Min length: 1, Max length: 63
        icon (str):
        name (str): Min length: 1, Max length: 63
        priority (int):
        created_by_id (str | Unset):
        guid (str | Unset):
    """

    feature: str
    icon: str
    name: str
    priority: int
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        feature = self.feature

        icon = self.icon

        name = self.name

        priority = self.priority

        created_by_id = self.created_by_id

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "feature": feature,
                "icon": icon,
                "name": name,
                "priority": priority,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        feature = d.pop("feature")

        icon = d.pop("icon")

        name = d.pop("name")

        priority = d.pop("priority")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        post_mission_groups = cls(
            feature=feature,
            icon=icon,
            name=name,
            priority=priority,
            created_by_id=created_by_id,
            guid=guid,
        )

        post_mission_groups.additional_properties = d
        return post_mission_groups

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
