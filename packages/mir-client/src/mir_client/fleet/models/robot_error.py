from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="RobotError")


@_attrs_define
class RobotError:
    """
    Attributes:
        code (int):
        description (str):
        module (str):
        timestamp (datetime.datetime):
    """

    code: int
    description: str
    module: str
    timestamp: datetime.datetime

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        description = self.description

        module = self.module

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "code": code,
                "description": description,
                "module": module,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        description = d.pop("description")

        module = d.pop("module")

        timestamp = datetime.datetime.fromisoformat(d.pop("timestamp"))

        robot_error = cls(
            code=code,
            description=description,
            module=module,
            timestamp=timestamp,
        )

        return robot_error
