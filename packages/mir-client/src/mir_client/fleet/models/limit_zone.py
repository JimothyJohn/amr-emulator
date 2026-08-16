from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="LimitZone")


@_attrs_define
class LimitZone:
    """
    Attributes:
        robot_limit (int | Unset):
    """

    robot_limit: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        robot_limit = self.robot_limit

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if robot_limit is not UNSET:
            field_dict["robot-limit"] = robot_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        robot_limit = d.pop("robot-limit", UNSET)

        limit_zone = cls(
            robot_limit=robot_limit,
        )

        return limit_zone
