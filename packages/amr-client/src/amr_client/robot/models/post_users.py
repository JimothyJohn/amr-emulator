from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostUsers")


@_attrs_define
class PostUsers:
    """
    Attributes:
        name (str): Min length: 2, Max length: 255
        password (str):
        user_group_id (str):
        username (str): Min length: 2, Max length: 63
        created_by_id (str | Unset):
        dashboard_id (str | Unset):
        email (str | Unset):
        guid (str | Unset):
        pincode (str | Unset):
        single_dashboard (bool | Unset):
    """

    name: str
    password: str
    user_group_id: str
    username: str
    created_by_id: str | Unset = UNSET
    dashboard_id: str | Unset = UNSET
    email: str | Unset = UNSET
    guid: str | Unset = UNSET
    pincode: str | Unset = UNSET
    single_dashboard: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        password = self.password

        user_group_id = self.user_group_id

        username = self.username

        created_by_id = self.created_by_id

        dashboard_id = self.dashboard_id

        email = self.email

        guid = self.guid

        pincode = self.pincode

        single_dashboard = self.single_dashboard

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "password": password,
                "user_group_id": user_group_id,
                "username": username,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if dashboard_id is not UNSET:
            field_dict["dashboard_id"] = dashboard_id
        if email is not UNSET:
            field_dict["email"] = email
        if guid is not UNSET:
            field_dict["guid"] = guid
        if pincode is not UNSET:
            field_dict["pincode"] = pincode
        if single_dashboard is not UNSET:
            field_dict["single_dashboard"] = single_dashboard

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        password = d.pop("password")

        user_group_id = d.pop("user_group_id")

        username = d.pop("username")

        created_by_id = d.pop("created_by_id", UNSET)

        dashboard_id = d.pop("dashboard_id", UNSET)

        email = d.pop("email", UNSET)

        guid = d.pop("guid", UNSET)

        pincode = d.pop("pincode", UNSET)

        single_dashboard = d.pop("single_dashboard", UNSET)

        post_users = cls(
            name=name,
            password=password,
            user_group_id=user_group_id,
            username=username,
            created_by_id=created_by_id,
            dashboard_id=dashboard_id,
            email=email,
            guid=guid,
            pincode=pincode,
            single_dashboard=single_dashboard,
        )

        post_users.additional_properties = d
        return post_users

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
