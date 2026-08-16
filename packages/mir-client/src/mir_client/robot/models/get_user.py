from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetUser")


@_attrs_define
class GetUser:
    """
    Attributes:
        create_time (str | Unset): Creation time of the user
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        dashboard_id (str | Unset):
        email (str | Unset): The email of the user
        guid (str | Unset): The global unique id across robots that identifies this user
        name (str | Unset): The name of the user
        pincode (str | Unset): Pincode for the user
        single_dashboard (bool | Unset):
        update_time (str | Unset): Last time the user was updated
        url (str | Unset): Url to this user
        user_group (str | Unset): Url for the user group this user is in
        user_group_id (str | Unset): Global id of the user group this user is in
        username (str | Unset): The username of the user
    """

    create_time: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    dashboard_id: str | Unset = UNSET
    email: str | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    pincode: str | Unset = UNSET
    single_dashboard: bool | Unset = UNSET
    update_time: str | Unset = UNSET
    url: str | Unset = UNSET
    user_group: str | Unset = UNSET
    user_group_id: str | Unset = UNSET
    username: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        create_time = self.create_time

        created_by = self.created_by

        created_by_id = self.created_by_id

        dashboard_id = self.dashboard_id

        email = self.email

        guid = self.guid

        name = self.name

        pincode = self.pincode

        single_dashboard = self.single_dashboard

        update_time = self.update_time

        url = self.url

        user_group = self.user_group

        user_group_id = self.user_group_id

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if create_time is not UNSET:
            field_dict["create_time"] = create_time
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if dashboard_id is not UNSET:
            field_dict["dashboard_id"] = dashboard_id
        if email is not UNSET:
            field_dict["email"] = email
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if pincode is not UNSET:
            field_dict["pincode"] = pincode
        if single_dashboard is not UNSET:
            field_dict["single_dashboard"] = single_dashboard
        if update_time is not UNSET:
            field_dict["update_time"] = update_time
        if url is not UNSET:
            field_dict["url"] = url
        if user_group is not UNSET:
            field_dict["user_group"] = user_group
        if user_group_id is not UNSET:
            field_dict["user_group_id"] = user_group_id
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        create_time = d.pop("create_time", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        dashboard_id = d.pop("dashboard_id", UNSET)

        email = d.pop("email", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        pincode = d.pop("pincode", UNSET)

        single_dashboard = d.pop("single_dashboard", UNSET)

        update_time = d.pop("update_time", UNSET)

        url = d.pop("url", UNSET)

        user_group = d.pop("user_group", UNSET)

        user_group_id = d.pop("user_group_id", UNSET)

        username = d.pop("username", UNSET)

        get_user = cls(
            create_time=create_time,
            created_by=created_by,
            created_by_id=created_by_id,
            dashboard_id=dashboard_id,
            email=email,
            guid=guid,
            name=name,
            pincode=pincode,
            single_dashboard=single_dashboard,
            update_time=update_time,
            url=url,
            user_group=user_group,
            user_group_id=user_group_id,
            username=username,
        )

        get_user.additional_properties = d
        return get_user

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
