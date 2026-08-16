from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetUserMePermissions")


@_attrs_define
class GetUserMePermissions:
    """
    Attributes:
        endpoint (str | Unset):
        guid (str | Unset): The global unique id across robots that identifies this permission
        permission_type (str | Unset): The permission type
        url (str | Unset): The URL of the resource
    """

    endpoint: str | Unset = UNSET
    guid: str | Unset = UNSET
    permission_type: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        endpoint = self.endpoint

        guid = self.guid

        permission_type = self.permission_type

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if endpoint is not UNSET:
            field_dict["endpoint"] = endpoint
        if guid is not UNSET:
            field_dict["guid"] = guid
        if permission_type is not UNSET:
            field_dict["permission_type"] = permission_type
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint = d.pop("endpoint", UNSET)

        guid = d.pop("guid", UNSET)

        permission_type = d.pop("permission_type", UNSET)

        url = d.pop("url", UNSET)

        get_user_me_permissions = cls(
            endpoint=endpoint,
            guid=guid,
            permission_type=permission_type,
            url=url,
        )

        get_user_me_permissions.additional_properties = d
        return get_user_me_permissions

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
