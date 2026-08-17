from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostElevatorFloors")


@_attrs_define
class PostElevatorFloors:
    """
    Attributes:
        door (int):
        elevator_entry_pos_guid (str):
        elevator_guid (str):
        elevator_pos_guid (str):
        floor (int):
        map_guid (str):
        created_by_id (str | Unset):
        entry_mission_guid (str | Unset):
        exit_mission_guid (str | Unset):
        guid (str | Unset):
    """

    door: int
    elevator_entry_pos_guid: str
    elevator_guid: str
    elevator_pos_guid: str
    floor: int
    map_guid: str
    created_by_id: str | Unset = UNSET
    entry_mission_guid: str | Unset = UNSET
    exit_mission_guid: str | Unset = UNSET
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        door = self.door

        elevator_entry_pos_guid = self.elevator_entry_pos_guid

        elevator_guid = self.elevator_guid

        elevator_pos_guid = self.elevator_pos_guid

        floor = self.floor

        map_guid = self.map_guid

        created_by_id = self.created_by_id

        entry_mission_guid = self.entry_mission_guid

        exit_mission_guid = self.exit_mission_guid

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "door": door,
                "elevator_entry_pos_guid": elevator_entry_pos_guid,
                "elevator_guid": elevator_guid,
                "elevator_pos_guid": elevator_pos_guid,
                "floor": floor,
                "map_guid": map_guid,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if entry_mission_guid is not UNSET:
            field_dict["entry_mission_guid"] = entry_mission_guid
        if exit_mission_guid is not UNSET:
            field_dict["exit_mission_guid"] = exit_mission_guid
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        door = d.pop("door")

        elevator_entry_pos_guid = d.pop("elevator_entry_pos_guid")

        elevator_guid = d.pop("elevator_guid")

        elevator_pos_guid = d.pop("elevator_pos_guid")

        floor = d.pop("floor")

        map_guid = d.pop("map_guid")

        created_by_id = d.pop("created_by_id", UNSET)

        entry_mission_guid = d.pop("entry_mission_guid", UNSET)

        exit_mission_guid = d.pop("exit_mission_guid", UNSET)

        guid = d.pop("guid", UNSET)

        post_elevator_floors = cls(
            door=door,
            elevator_entry_pos_guid=elevator_entry_pos_guid,
            elevator_guid=elevator_guid,
            elevator_pos_guid=elevator_pos_guid,
            floor=floor,
            map_guid=map_guid,
            created_by_id=created_by_id,
            entry_mission_guid=entry_mission_guid,
            exit_mission_guid=exit_mission_guid,
            guid=guid,
        )

        post_elevator_floors.additional_properties = d
        return post_elevator_floors

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
