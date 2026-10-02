from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutMission")


@_attrs_define
class PutMission:
    """
    Attributes:
        description (str | Unset): Max length: 255
        group_id (str | Unset):
        hidden (bool | Unset):
        name (str | Unset): Min length: 1, Max length: 255
        session_id (str | Unset):
    """

    description: str | Unset = UNSET
    group_id: str | Unset = UNSET
    hidden: bool | Unset = UNSET
    name: str | Unset = UNSET
    session_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        group_id = self.group_id

        hidden = self.hidden

        name = self.name

        session_id = self.session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if hidden is not UNSET:
            field_dict["hidden"] = hidden
        if name is not UNSET:
            field_dict["name"] = name
        if session_id is not UNSET:
            field_dict["session_id"] = session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description", UNSET)

        group_id = d.pop("group_id", UNSET)

        hidden = d.pop("hidden", UNSET)

        name = d.pop("name", UNSET)

        session_id = d.pop("session_id", UNSET)

        put_mission = cls(
            description=description,
            group_id=group_id,
            hidden=hidden,
            name=name,
            session_id=session_id,
        )

        put_mission.additional_properties = d
        return put_mission

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
