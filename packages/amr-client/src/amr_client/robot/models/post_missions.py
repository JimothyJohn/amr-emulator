from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostMissions")


@_attrs_define
class PostMissions:
    """
    Attributes:
        group_id (str):
        name (str): Min length: 1, Max length: 255
        created_by_id (str | Unset):
        description (str | Unset): Max length: 255
        guid (str | Unset):
        hidden (bool | Unset):
        session_id (str | Unset):
    """

    group_id: str
    name: str
    created_by_id: str | Unset = UNSET
    description: str | Unset = UNSET
    guid: str | Unset = UNSET
    hidden: bool | Unset = UNSET
    session_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_id = self.group_id

        name = self.name

        created_by_id = self.created_by_id

        description = self.description

        guid = self.guid

        hidden = self.hidden

        session_id = self.session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "group_id": group_id,
                "name": name,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if description is not UNSET:
            field_dict["description"] = description
        if guid is not UNSET:
            field_dict["guid"] = guid
        if hidden is not UNSET:
            field_dict["hidden"] = hidden
        if session_id is not UNSET:
            field_dict["session_id"] = session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        group_id = d.pop("group_id")

        name = d.pop("name")

        created_by_id = d.pop("created_by_id", UNSET)

        description = d.pop("description", UNSET)

        guid = d.pop("guid", UNSET)

        hidden = d.pop("hidden", UNSET)

        session_id = d.pop("session_id", UNSET)

        post_missions = cls(
            group_id=group_id,
            name=name,
            created_by_id=created_by_id,
            description=description,
            guid=guid,
            hidden=hidden,
            session_id=session_id,
        )

        post_missions.additional_properties = d
        return post_missions

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
