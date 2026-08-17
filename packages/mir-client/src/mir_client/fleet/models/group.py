from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """
    Attributes:
        name (str):
        id (None | Unset | UUID):
        robot_ids (list[str] | None | Unset):
        position_ids (list[str] | None | Unset):
        mission_group_ids (list[str] | None | Unset):
    """

    name: str
    id: None | Unset | UUID = UNSET
    robot_ids: list[str] | None | Unset = UNSET
    position_ids: list[str] | None | Unset = UNSET
    mission_group_ids: list[str] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        elif isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        robot_ids: list[str] | None | Unset
        if isinstance(self.robot_ids, Unset):
            robot_ids = UNSET
        elif isinstance(self.robot_ids, list):
            robot_ids = self.robot_ids

        else:
            robot_ids = self.robot_ids

        position_ids: list[str] | None | Unset
        if isinstance(self.position_ids, Unset):
            position_ids = UNSET
        elif isinstance(self.position_ids, list):
            position_ids = self.position_ids

        else:
            position_ids = self.position_ids

        mission_group_ids: list[str] | None | Unset
        if isinstance(self.mission_group_ids, Unset):
            mission_group_ids = UNSET
        elif isinstance(self.mission_group_ids, list):
            mission_group_ids = self.mission_group_ids

        else:
            mission_group_ids = self.mission_group_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
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
        name = d.pop("name")

        def _parse_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                id_type_0 = UUID(data)

                return id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_robot_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                robot_ids_type_0 = cast(list[str], data)

                return robot_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        robot_ids = _parse_robot_ids(d.pop("robot-ids", UNSET))

        def _parse_position_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                position_ids_type_0 = cast(list[str], data)

                return position_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        position_ids = _parse_position_ids(d.pop("position-ids", UNSET))

        def _parse_mission_group_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                mission_group_ids_type_0 = cast(list[str], data)

                return mission_group_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        mission_group_ids = _parse_mission_group_ids(d.pop("mission-group-ids", UNSET))

        group = cls(
            name=name,
            id=id,
            robot_ids=robot_ids,
            position_ids=position_ids,
            mission_group_ids=mission_group_ids,
        )

        return group
