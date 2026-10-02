from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutElevatorFloor")


@_attrs_define
class PutElevatorFloor:
    """
    Attributes:
        door (int | Unset):
        elevator_entry_pos_guid (str | Unset):
        elevator_guid (str | Unset):
        elevator_pos_guid (str | Unset):
        entry_mission_guid (str | Unset):
        exit_mission_guid (str | Unset):
        floor (int | Unset):
        map_guid (str | Unset):
    """

    door: int | Unset = UNSET
    elevator_entry_pos_guid: str | Unset = UNSET
    elevator_guid: str | Unset = UNSET
    elevator_pos_guid: str | Unset = UNSET
    entry_mission_guid: str | Unset = UNSET
    exit_mission_guid: str | Unset = UNSET
    floor: int | Unset = UNSET
    map_guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        door = self.door

        elevator_entry_pos_guid = self.elevator_entry_pos_guid

        elevator_guid = self.elevator_guid

        elevator_pos_guid = self.elevator_pos_guid

        entry_mission_guid = self.entry_mission_guid

        exit_mission_guid = self.exit_mission_guid

        floor = self.floor

        map_guid = self.map_guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if door is not UNSET:
            field_dict["door"] = door
        if elevator_entry_pos_guid is not UNSET:
            field_dict["elevator_entry_pos_guid"] = elevator_entry_pos_guid
        if elevator_guid is not UNSET:
            field_dict["elevator_guid"] = elevator_guid
        if elevator_pos_guid is not UNSET:
            field_dict["elevator_pos_guid"] = elevator_pos_guid
        if entry_mission_guid is not UNSET:
            field_dict["entry_mission_guid"] = entry_mission_guid
        if exit_mission_guid is not UNSET:
            field_dict["exit_mission_guid"] = exit_mission_guid
        if floor is not UNSET:
            field_dict["floor"] = floor
        if map_guid is not UNSET:
            field_dict["map_guid"] = map_guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        door = d.pop("door", UNSET)

        elevator_entry_pos_guid = d.pop("elevator_entry_pos_guid", UNSET)

        elevator_guid = d.pop("elevator_guid", UNSET)

        elevator_pos_guid = d.pop("elevator_pos_guid", UNSET)

        entry_mission_guid = d.pop("entry_mission_guid", UNSET)

        exit_mission_guid = d.pop("exit_mission_guid", UNSET)

        floor = d.pop("floor", UNSET)

        map_guid = d.pop("map_guid", UNSET)

        put_elevator_floor = cls(
            door=door,
            elevator_entry_pos_guid=elevator_entry_pos_guid,
            elevator_guid=elevator_guid,
            elevator_pos_guid=elevator_pos_guid,
            entry_mission_guid=entry_mission_guid,
            exit_mission_guid=exit_mission_guid,
            floor=floor,
            map_guid=map_guid,
        )

        put_elevator_floor.additional_properties = d
        return put_elevator_floor

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
