from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Robot")


@_attrs_define
class Robot:
    """
    Attributes:
        robot_id (str | Unset):
        robot_state (str | Unset):
    """

    robot_id: str | Unset = UNSET
    robot_state: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        robot_id = self.robot_id

        robot_state = self.robot_state

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id
        if robot_state is not UNSET:
            field_dict["robot-state"] = robot_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        robot_id = d.pop("robot-id", UNSET)

        robot_state = d.pop("robot-state", UNSET)

        robot = cls(
            robot_id=robot_id,
            robot_state=robot_state,
        )

        return robot
