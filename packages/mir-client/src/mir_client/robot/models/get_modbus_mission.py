from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetModbusMission")


@_attrs_define
class GetModbusMission:
    """
    Attributes:
        coil_id (int | Unset): The id of the coil to trigger the mission
        created_by (str | Unset): The url to the description of the type of this modbus mission
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global id unique across robots that identifies this modbus mission
        id (int | Unset): The id of the modbus mission entry
        mission (str | Unset): The url to the mission details
        mission_id (str | Unset): The global id of the mission that was executed
        name (str | Unset): A more detailed explanation of the attribute
        parameters (str | Unset):
    """

    coil_id: int | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    id: int | Unset = UNSET
    mission: str | Unset = UNSET
    mission_id: str | Unset = UNSET
    name: str | Unset = UNSET
    parameters: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        coil_id = self.coil_id

        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        id = self.id

        mission = self.mission

        mission_id = self.mission_id

        name = self.name

        parameters = self.parameters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if coil_id is not UNSET:
            field_dict["coil_id"] = coil_id
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if id is not UNSET:
            field_dict["id"] = id
        if mission is not UNSET:
            field_dict["mission"] = mission
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if name is not UNSET:
            field_dict["name"] = name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        coil_id = d.pop("coil_id", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        id = d.pop("id", UNSET)

        mission = d.pop("mission", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        name = d.pop("name", UNSET)

        parameters = d.pop("parameters", UNSET)

        get_modbus_mission = cls(
            coil_id=coil_id,
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            id=id,
            mission=mission,
            mission_id=mission_id,
            name=name,
            parameters=parameters,
        )

        get_modbus_mission.additional_properties = d
        return get_modbus_mission

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
