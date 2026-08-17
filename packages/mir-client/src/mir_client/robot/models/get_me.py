from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMe")


@_attrs_define
class GetMe:
    """
    Attributes:
        guid (str | Unset): The global unique id across robots that identifies this user
        name (str | Unset): The name of the user
        url (str | Unset): The URL of the resource
        user_group (str | Unset): Url for the user group this user is in
        user_group_id (str | Unset): Global id of the user group this user is in
    """

    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    url: str | Unset = UNSET
    user_group: str | Unset = UNSET
    user_group_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        name = self.name

        url = self.url

        user_group = self.user_group

        user_group_id = self.user_group_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url
        if user_group is not UNSET:
            field_dict["user_group"] = user_group
        if user_group_id is not UNSET:
            field_dict["user_group_id"] = user_group_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        user_group = d.pop("user_group", UNSET)

        user_group_id = d.pop("user_group_id", UNSET)

        get_me = cls(
            guid=guid,
            name=name,
            url=url,
            user_group=user_group,
            user_group_id=user_group_id,
        )

        get_me.additional_properties = d
        return get_me

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
