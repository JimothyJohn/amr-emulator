from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPositionTransitionLists")


@_attrs_define
class GetPositionTransitionLists:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        goal_pos_id (str | Unset): The id of the end position for the transition list
        guid (str | Unset): The global id unique across robots that identifies this path
        mission_id (str | Unset): The guid of the mission in the transition list
        start_pos_id (str | Unset): The id of the start position for the transition list
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    goal_pos_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    mission_id: str | Unset = UNSET
    start_pos_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        goal_pos_id = self.goal_pos_id

        guid = self.guid

        mission_id = self.mission_id

        start_pos_id = self.start_pos_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if goal_pos_id is not UNSET:
            field_dict["goal_pos_id"] = goal_pos_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if start_pos_id is not UNSET:
            field_dict["start_pos_id"] = start_pos_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        goal_pos_id = d.pop("goal_pos_id", UNSET)

        guid = d.pop("guid", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        start_pos_id = d.pop("start_pos_id", UNSET)

        get_position_transition_lists = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            goal_pos_id=goal_pos_id,
            guid=guid,
            mission_id=mission_id,
            start_pos_id=start_pos_id,
        )

        get_position_transition_lists.additional_properties = d
        return get_position_transition_lists

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
