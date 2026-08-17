from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="ContinueRequest")


@_attrs_define
class ContinueRequest:
    """
    Attributes:
        robot_id (UUID):
    """

    robot_id: UUID

    def to_dict(self) -> dict[str, Any]:
        robot_id = str(self.robot_id)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "robot-id": robot_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        robot_id = UUID(d.pop("robot-id"))

        continue_request = cls(
            robot_id=robot_id,
        )

        return continue_request
