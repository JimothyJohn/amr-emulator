from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutMissionQueue")


@_attrs_define
class PutMissionQueue:
    """
    Attributes:
        cmd (int | Unset):
        mission_id (str | Unset):
        priority (int | Unset):
    """

    cmd: int | Unset = UNSET
    mission_id: str | Unset = UNSET
    priority: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cmd = self.cmd

        mission_id = self.mission_id

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cmd is not UNSET:
            field_dict["cmd"] = cmd
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cmd = d.pop("cmd", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        priority = d.pop("priority", UNSET)

        put_mission_queue = cls(
            cmd=cmd,
            mission_id=mission_id,
            priority=priority,
        )

        put_mission_queue.additional_properties = d
        return put_mission_queue

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
