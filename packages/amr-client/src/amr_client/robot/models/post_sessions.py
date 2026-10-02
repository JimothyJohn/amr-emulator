from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSessions")


@_attrs_define
class PostSessions:
    """
    Attributes:
        name (str): Min length: 1, Max length: 40
        created_by_id (str | Unset):
        description (str | Unset): Max length: 255
        guid (str | Unset):
    """

    name: str
    created_by_id: str | Unset = UNSET
    description: str | Unset = UNSET
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        created_by_id = self.created_by_id

        description = self.description

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if description is not UNSET:
            field_dict["description"] = description
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        created_by_id = d.pop("created_by_id", UNSET)

        description = d.pop("description", UNSET)

        guid = d.pop("guid", UNSET)

        post_sessions = cls(
            name=name,
            created_by_id=created_by_id,
            description=description,
            guid=guid,
        )

        post_sessions.additional_properties = d
        return post_sessions

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
