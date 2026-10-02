from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutPositionTransitionList")


@_attrs_define
class PutPositionTransitionList:
    """
    Attributes:
        goal_pos_id (str | Unset):
        mission_id (str | Unset):
        start_pos_id (str | Unset):
    """

    goal_pos_id: str | Unset = UNSET
    mission_id: str | Unset = UNSET
    start_pos_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        goal_pos_id = self.goal_pos_id

        mission_id = self.mission_id

        start_pos_id = self.start_pos_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if goal_pos_id is not UNSET:
            field_dict["goal_pos_id"] = goal_pos_id
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if start_pos_id is not UNSET:
            field_dict["start_pos_id"] = start_pos_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        goal_pos_id = d.pop("goal_pos_id", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        start_pos_id = d.pop("start_pos_id", UNSET)

        put_position_transition_list = cls(
            goal_pos_id=goal_pos_id,
            mission_id=mission_id,
            start_pos_id=start_pos_id,
        )

        put_position_transition_list.additional_properties = d
        return put_position_transition_list

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
