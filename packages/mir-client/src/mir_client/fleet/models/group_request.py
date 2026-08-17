from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.group import Group


T = TypeVar("T", bound="GroupRequest")


@_attrs_define
class GroupRequest:
    """
    Attributes:
        group (Group):
    """

    group: Group

    def to_dict(self) -> dict[str, Any]:
        group = self.group.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "group": group,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group import Group

        d = dict(src_dict)
        group = Group.from_dict(d.pop("group"))

        group_request = cls(
            group=group,
        )

        return group_request
