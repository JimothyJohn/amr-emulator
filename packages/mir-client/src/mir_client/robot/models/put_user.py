from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutUser")


@_attrs_define
class PutUser:
    """
    Attributes:
        dashboard_id (str | Unset):
        email (str | Unset):
        name (str | Unset): Min length: 2, Max length: 255
        password (str | Unset):
        pincode (str | Unset):
        single_dashboard (bool | Unset):
        user_group_id (str | Unset):
        username (str | Unset): Min length: 2, Max length: 63
    """

    dashboard_id: str | Unset = UNSET
    email: str | Unset = UNSET
    name: str | Unset = UNSET
    password: str | Unset = UNSET
    pincode: str | Unset = UNSET
    single_dashboard: bool | Unset = UNSET
    user_group_id: str | Unset = UNSET
    username: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dashboard_id = self.dashboard_id

        email = self.email

        name = self.name

        password = self.password

        pincode = self.pincode

        single_dashboard = self.single_dashboard

        user_group_id = self.user_group_id

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dashboard_id is not UNSET:
            field_dict["dashboard_id"] = dashboard_id
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name
        if password is not UNSET:
            field_dict["password"] = password
        if pincode is not UNSET:
            field_dict["pincode"] = pincode
        if single_dashboard is not UNSET:
            field_dict["single_dashboard"] = single_dashboard
        if user_group_id is not UNSET:
            field_dict["user_group_id"] = user_group_id
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dashboard_id = d.pop("dashboard_id", UNSET)

        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        password = d.pop("password", UNSET)

        pincode = d.pop("pincode", UNSET)

        single_dashboard = d.pop("single_dashboard", UNSET)

        user_group_id = d.pop("user_group_id", UNSET)

        username = d.pop("username", UNSET)

        put_user = cls(
            dashboard_id=dashboard_id,
            email=email,
            name=name,
            password=password,
            pincode=pincode,
            single_dashboard=single_dashboard,
            user_group_id=user_group_id,
            username=username,
        )

        put_user.additional_properties = d
        return put_user

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
