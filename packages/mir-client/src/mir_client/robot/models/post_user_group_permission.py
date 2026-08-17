from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostUserGroupPermission")


@_attrs_define
class PostUserGroupPermission:
    """
    Attributes:
        endpoint (str): Min length: 1, Max length: 255
        permission_type (str):
        user_group_guid (str):
        guid (str | Unset):
    """

    endpoint: str
    permission_type: str
    user_group_guid: str
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        endpoint = self.endpoint

        permission_type = self.permission_type

        user_group_guid = self.user_group_guid

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "endpoint": endpoint,
                "permission_type": permission_type,
                "user_group_guid": user_group_guid,
            }
        )
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint = d.pop("endpoint")

        permission_type = d.pop("permission_type")

        user_group_guid = d.pop("user_group_guid")

        guid = d.pop("guid", UNSET)

        post_user_group_permission = cls(
            endpoint=endpoint,
            permission_type=permission_type,
            user_group_guid=user_group_guid,
            guid=guid,
        )

        post_user_group_permission.additional_properties = d
        return post_user_group_permission

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
