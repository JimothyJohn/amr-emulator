from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="MissionGroup")


@_attrs_define
class MissionGroup:
    """
    Attributes:
        name (str | Unset):
        mission_ids (list[str] | Unset):
    """

    name: str | Unset = UNSET
    mission_ids: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        mission_ids: list[str] | Unset = UNSET
        if not isinstance(self.mission_ids, Unset):
            mission_ids = self.mission_ids

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if mission_ids is not UNSET:
            field_dict["mission-ids"] = mission_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        mission_ids = cast(list[str], d.pop("mission-ids", UNSET))

        mission_group = cls(
            name=name,
            mission_ids=mission_ids,
        )

        return mission_group
