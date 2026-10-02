from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostUserGroups")


@_attrs_define
class PostUserGroups:
    """
    Attributes:
        name (str): Min length: 2, Max length: 255
        created_by_id (str | Unset):
        guid (str | Unset):
        session_expiration_enabled (bool | Unset):
        session_timeout (int | Unset):
    """

    name: str
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    session_expiration_enabled: bool | Unset = UNSET
    session_timeout: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        created_by_id = self.created_by_id

        guid = self.guid

        session_expiration_enabled = self.session_expiration_enabled

        session_timeout = self.session_timeout

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if session_expiration_enabled is not UNSET:
            field_dict["session_expiration_enabled"] = session_expiration_enabled
        if session_timeout is not UNSET:
            field_dict["session_timeout"] = session_timeout

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        session_expiration_enabled = d.pop("session_expiration_enabled", UNSET)

        session_timeout = d.pop("session_timeout", UNSET)

        post_user_groups = cls(
            name=name,
            created_by_id=created_by_id,
            guid=guid,
            session_expiration_enabled=session_expiration_enabled,
            session_timeout=session_timeout,
        )

        post_user_groups.additional_properties = d
        return post_user_groups

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
