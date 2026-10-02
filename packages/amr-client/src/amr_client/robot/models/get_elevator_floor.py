from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetElevatorFloor")


@_attrs_define
class GetElevatorFloor:
    """
    Attributes:
        created_by (str | Unset): The url to the description this elevator floor
        created_by_id (str | Unset): The global id of the user who created this entry
        door (int | Unset): The integer identifying the door used by the elevator on this floor
        elevator_entry_pos (str | Unset):
        elevator_entry_pos_guid (str | Unset): The id of the position located in front of the elevator
        elevator_guid (str | Unset): The global unique id of the elevator associated with this floor
        elevator_pos (str | Unset):
        elevator_pos_guid (str | Unset): The id of the position located in the elevator
        entry_mission (str | Unset):
        entry_mission_guid (str | Unset): The id of the entry mission
        exit_mission (str | Unset):
        exit_mission_guid (str | Unset): The id of the exit mission
        floor (int | Unset): The integer identifying the floor
        guid (str | Unset): The global id unique across robots that identifies this elevator floor
        map_ (str | Unset):
        map_guid (str | Unset): The map id associated with the floor
        session_guid (str | Unset): The global id unique across robots containing this elevator
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    door: int | Unset = UNSET
    elevator_entry_pos: str | Unset = UNSET
    elevator_entry_pos_guid: str | Unset = UNSET
    elevator_guid: str | Unset = UNSET
    elevator_pos: str | Unset = UNSET
    elevator_pos_guid: str | Unset = UNSET
    entry_mission: str | Unset = UNSET
    entry_mission_guid: str | Unset = UNSET
    exit_mission: str | Unset = UNSET
    exit_mission_guid: str | Unset = UNSET
    floor: int | Unset = UNSET
    guid: str | Unset = UNSET
    map_: str | Unset = UNSET
    map_guid: str | Unset = UNSET
    session_guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        door = self.door

        elevator_entry_pos = self.elevator_entry_pos

        elevator_entry_pos_guid = self.elevator_entry_pos_guid

        elevator_guid = self.elevator_guid

        elevator_pos = self.elevator_pos

        elevator_pos_guid = self.elevator_pos_guid

        entry_mission = self.entry_mission

        entry_mission_guid = self.entry_mission_guid

        exit_mission = self.exit_mission

        exit_mission_guid = self.exit_mission_guid

        floor = self.floor

        guid = self.guid

        map_ = self.map_

        map_guid = self.map_guid

        session_guid = self.session_guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if door is not UNSET:
            field_dict["door"] = door
        if elevator_entry_pos is not UNSET:
            field_dict["elevator_entry_pos"] = elevator_entry_pos
        if elevator_entry_pos_guid is not UNSET:
            field_dict["elevator_entry_pos_guid"] = elevator_entry_pos_guid
        if elevator_guid is not UNSET:
            field_dict["elevator_guid"] = elevator_guid
        if elevator_pos is not UNSET:
            field_dict["elevator_pos"] = elevator_pos
        if elevator_pos_guid is not UNSET:
            field_dict["elevator_pos_guid"] = elevator_pos_guid
        if entry_mission is not UNSET:
            field_dict["entry_mission"] = entry_mission
        if entry_mission_guid is not UNSET:
            field_dict["entry_mission_guid"] = entry_mission_guid
        if exit_mission is not UNSET:
            field_dict["exit_mission"] = exit_mission
        if exit_mission_guid is not UNSET:
            field_dict["exit_mission_guid"] = exit_mission_guid
        if floor is not UNSET:
            field_dict["floor"] = floor
        if guid is not UNSET:
            field_dict["guid"] = guid
        if map_ is not UNSET:
            field_dict["map"] = map_
        if map_guid is not UNSET:
            field_dict["map_guid"] = map_guid
        if session_guid is not UNSET:
            field_dict["session_guid"] = session_guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        door = d.pop("door", UNSET)

        elevator_entry_pos = d.pop("elevator_entry_pos", UNSET)

        elevator_entry_pos_guid = d.pop("elevator_entry_pos_guid", UNSET)

        elevator_guid = d.pop("elevator_guid", UNSET)

        elevator_pos = d.pop("elevator_pos", UNSET)

        elevator_pos_guid = d.pop("elevator_pos_guid", UNSET)

        entry_mission = d.pop("entry_mission", UNSET)

        entry_mission_guid = d.pop("entry_mission_guid", UNSET)

        exit_mission = d.pop("exit_mission", UNSET)

        exit_mission_guid = d.pop("exit_mission_guid", UNSET)

        floor = d.pop("floor", UNSET)

        guid = d.pop("guid", UNSET)

        map_ = d.pop("map", UNSET)

        map_guid = d.pop("map_guid", UNSET)

        session_guid = d.pop("session_guid", UNSET)

        get_elevator_floor = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            door=door,
            elevator_entry_pos=elevator_entry_pos,
            elevator_entry_pos_guid=elevator_entry_pos_guid,
            elevator_guid=elevator_guid,
            elevator_pos=elevator_pos,
            elevator_pos_guid=elevator_pos_guid,
            entry_mission=entry_mission,
            entry_mission_guid=entry_mission_guid,
            exit_mission=exit_mission,
            exit_mission_guid=exit_mission_guid,
            floor=floor,
            guid=guid,
            map_=map_,
            map_guid=map_guid,
            session_guid=session_guid,
        )

        get_elevator_floor.additional_properties = d
        return get_elevator_floor

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
