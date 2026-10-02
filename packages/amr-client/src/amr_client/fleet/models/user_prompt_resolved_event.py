from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserPromptResolvedEvent")


@_attrs_define
class UserPromptResolvedEvent:
    """
    Attributes:
        id (str | Unset):
        robot_id (str | Unset):
    """

    id: str | Unset = UNSET
    robot_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        robot_id = self.robot_id

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        robot_id = d.pop("robot-id", UNSET)

        user_prompt_resolved_event = cls(
            id=id,
            robot_id=robot_id,
        )

        return user_prompt_resolved_event
