from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="MissionsExportRequest")


@_attrs_define
class MissionsExportRequest:
    """
    Attributes:
        mission_ids (list[UUID]):
        mission_group_ids (list[UUID]):
    """

    mission_ids: list[UUID]
    mission_group_ids: list[UUID]

    def to_dict(self) -> dict[str, Any]:
        mission_ids = []
        for mission_ids_item_data in self.mission_ids:
            mission_ids_item = str(mission_ids_item_data)
            mission_ids.append(mission_ids_item)

        mission_group_ids = []
        for mission_group_ids_item_data in self.mission_group_ids:
            mission_group_ids_item = str(mission_group_ids_item_data)
            mission_group_ids.append(mission_group_ids_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mission-ids": mission_ids,
                "mission-group-ids": mission_group_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mission_ids = []
        _mission_ids = d.pop("mission-ids")
        for mission_ids_item_data in _mission_ids:
            mission_ids_item = UUID(mission_ids_item_data)

            mission_ids.append(mission_ids_item)

        mission_group_ids = []
        _mission_group_ids = d.pop("mission-group-ids")
        for mission_group_ids_item_data in _mission_group_ids:
            mission_group_ids_item = UUID(mission_group_ids_item_data)

            mission_group_ids.append(mission_group_ids_item)

        missions_export_request = cls(
            mission_ids=mission_ids,
            mission_group_ids=mission_group_ids,
        )

        return missions_export_request
