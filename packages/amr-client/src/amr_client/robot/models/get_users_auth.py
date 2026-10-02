from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetUsersAuth")


@_attrs_define
class GetUsersAuth:
    """
    Attributes:
        expiration_time (datetime.datetime | Unset):
        ip (str | Unset):
        login_time (datetime.datetime | Unset):
        token (str | Unset):
        user_id (str | Unset):
    """

    expiration_time: datetime.datetime | Unset = UNSET
    ip: str | Unset = UNSET
    login_time: datetime.datetime | Unset = UNSET
    token: str | Unset = UNSET
    user_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expiration_time: str | Unset = UNSET
        if not isinstance(self.expiration_time, Unset):
            expiration_time = self.expiration_time.isoformat()

        ip = self.ip

        login_time: str | Unset = UNSET
        if not isinstance(self.login_time, Unset):
            login_time = self.login_time.isoformat()

        token = self.token

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expiration_time is not UNSET:
            field_dict["expiration_time"] = expiration_time
        if ip is not UNSET:
            field_dict["ip"] = ip
        if login_time is not UNSET:
            field_dict["login_time"] = login_time
        if token is not UNSET:
            field_dict["token"] = token
        if user_id is not UNSET:
            field_dict["user_id"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _expiration_time = d.pop("expiration_time", UNSET)
        expiration_time: datetime.datetime | Unset
        if isinstance(_expiration_time, Unset):
            expiration_time = UNSET
        else:
            expiration_time = datetime.datetime.fromisoformat(_expiration_time)

        ip = d.pop("ip", UNSET)

        _login_time = d.pop("login_time", UNSET)
        login_time: datetime.datetime | Unset
        if isinstance(_login_time, Unset):
            login_time = UNSET
        else:
            login_time = datetime.datetime.fromisoformat(_login_time)

        token = d.pop("token", UNSET)

        user_id = d.pop("user_id", UNSET)

        get_users_auth = cls(
            expiration_time=expiration_time,
            ip=ip,
            login_time=login_time,
            token=token,
            user_id=user_id,
        )

        get_users_auth.additional_properties = d
        return get_users_auth

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
