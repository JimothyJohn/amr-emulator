from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Group1")


@_attrs_define
class Group1:
    """
    Attributes:
        name (str | Unset):
        robot_ids (list[str] | Unset):
        position_ids (list[str] | Unset):
        mission_group_ids (list[str] | Unset):
    """

    name: str | Unset = UNSET
    robot_ids: list[str] | Unset = UNSET
    position_ids: list[str] | Unset = UNSET
    mission_group_ids: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        robot_ids: list[str] | Unset = UNSET
        if not isinstance(self.robot_ids, Unset):
            robot_ids = self.robot_ids

        position_ids: list[str] | Unset = UNSET
        if not isinstance(self.position_ids, Unset):
            position_ids = self.position_ids

        mission_group_ids: list[str] | Unset = UNSET
        if not isinstance(self.mission_group_ids, Unset):
            mission_group_ids = self.mission_group_ids

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if robot_ids is not UNSET:
            field_dict["robot-ids"] = robot_ids
        if position_ids is not UNSET:
            field_dict["position-ids"] = position_ids
        if mission_group_ids is not UNSET:
            field_dict["mission-group-ids"] = mission_group_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        robot_ids = cast(list[str], d.pop("robot-ids", UNSET))

        position_ids = cast(list[str], d.pop("position-ids", UNSET))

        mission_group_ids = cast(list[str], d.pop("mission-group-ids", UNSET))

        group_1 = cls(
            name=name,
            robot_ids=robot_ids,
            position_ids=position_ids,
            mission_group_ids=mission_group_ids,
        )

        return group_1
