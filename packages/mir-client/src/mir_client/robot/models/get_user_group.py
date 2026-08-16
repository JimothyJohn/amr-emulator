from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetUserGroup")


@_attrs_define
class GetUserGroup:
    """
    Attributes:
        create_time (str | Unset): Creation time of the usergroup
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global unique id across robots that identifies this usergroup
        name (str | Unset): Name of the usergroup
        session_expiration_enabled (bool | Unset): Session expiration enabled
        session_timeout (int | Unset): Session expiration timeout
        update_time (str | Unset): Last time the usergroup was updated
    """

    create_time: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    session_expiration_enabled: bool | Unset = UNSET
    session_timeout: int | Unset = UNSET
    update_time: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        create_time = self.create_time

        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        name = self.name

        session_expiration_enabled = self.session_expiration_enabled

        session_timeout = self.session_timeout

        update_time = self.update_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if create_time is not UNSET:
            field_dict["create_time"] = create_time
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if session_expiration_enabled is not UNSET:
            field_dict["session_expiration_enabled"] = session_expiration_enabled
        if session_timeout is not UNSET:
            field_dict["session_timeout"] = session_timeout
        if update_time is not UNSET:
            field_dict["update_time"] = update_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        create_time = d.pop("create_time", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        session_expiration_enabled = d.pop("session_expiration_enabled", UNSET)

        session_timeout = d.pop("session_timeout", UNSET)

        update_time = d.pop("update_time", UNSET)

        get_user_group = cls(
            create_time=create_time,
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            name=name,
            session_expiration_enabled=session_expiration_enabled,
            session_timeout=session_timeout,
            update_time=update_time,
        )

        get_user_group.additional_properties = d
        return get_user_group

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
