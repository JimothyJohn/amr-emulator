from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMissionGroup")


@_attrs_define
class GetMissionGroup:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        feature (str | Unset): The name of the position
        guid (str | Unset): The global id unique across robots that identifies this position
        icon (str | Unset): The name of the position
        name (str | Unset): The name of the position
        priority (int | Unset): The name of the position
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    feature: str | Unset = UNSET
    guid: str | Unset = UNSET
    icon: str | Unset = UNSET
    name: str | Unset = UNSET
    priority: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        feature = self.feature

        guid = self.guid

        icon = self.icon

        name = self.name

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if feature is not UNSET:
            field_dict["feature"] = feature
        if guid is not UNSET:
            field_dict["guid"] = guid
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
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        feature = d.pop("feature", UNSET)

        guid = d.pop("guid", UNSET)

        icon = d.pop("icon", UNSET)

        name = d.pop("name", UNSET)

        priority = d.pop("priority", UNSET)

        get_mission_group = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            feature=feature,
            guid=guid,
            icon=icon,
            name=name,
            priority=priority,
        )

        get_mission_group.additional_properties = d
        return get_mission_group

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
