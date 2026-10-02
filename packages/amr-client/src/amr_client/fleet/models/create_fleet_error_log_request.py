from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CreateFleetErrorLogRequest")


@_attrs_define
class CreateFleetErrorLogRequest:
    """
    Attributes:
        comment (str):
    """

    comment: str

    def to_dict(self) -> dict[str, Any]:
        comment = self.comment

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "comment": comment,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        comment = d.pop("comment")

        create_fleet_error_log_request = cls(
            comment=comment,
        )

        return create_fleet_error_log_request
