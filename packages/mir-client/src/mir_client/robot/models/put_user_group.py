from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutUserGroup")


@_attrs_define
class PutUserGroup:
    """
    Attributes:
        name (str | Unset): Min length: 2, Max length: 255
        session_expiration_enabled (bool | Unset):
        session_timeout (int | Unset):
    """

    name: str | Unset = UNSET
    session_expiration_enabled: bool | Unset = UNSET
    session_timeout: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        session_expiration_enabled = self.session_expiration_enabled

        session_timeout = self.session_timeout

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if session_expiration_enabled is not UNSET:
            field_dict["session_expiration_enabled"] = session_expiration_enabled
        if session_timeout is not UNSET:
            field_dict["session_timeout"] = session_timeout

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        session_expiration_enabled = d.pop("session_expiration_enabled", UNSET)

        session_timeout = d.pop("session_timeout", UNSET)

        put_user_group = cls(
            name=name,
            session_expiration_enabled=session_expiration_enabled,
            session_timeout=session_timeout,
        )

        put_user_group.additional_properties = d
        return put_user_group

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
