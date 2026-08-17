from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMissionAction")


@_attrs_define
class GetMissionAction:
    """
    Attributes:
        action_type (str | Unset): The id of the type of action
        created_by_id (str | Unset): User guid of the user of the mission which the action belongs to
        guid (str | Unset): The global id unique across robots that identifies this mission
        mission_id (str | Unset): The id of the mission the action belongs to
        parameters (str | Unset):
        priority (int | Unset): The priority of the action
        scope_reference (str | Unset): Reference to the scope in which the action belongs
    """

    action_type: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    mission_id: str | Unset = UNSET
    parameters: str | Unset = UNSET
    priority: int | Unset = UNSET
    scope_reference: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_type = self.action_type

        created_by_id = self.created_by_id

        guid = self.guid

        mission_id = self.mission_id

        parameters = self.parameters

        priority = self.priority

        scope_reference = self.scope_reference

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_type is not UNSET:
            field_dict["action_type"] = action_type
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if priority is not UNSET:
            field_dict["priority"] = priority
        if scope_reference is not UNSET:
            field_dict["scope_reference"] = scope_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action_type = d.pop("action_type", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        parameters = d.pop("parameters", UNSET)

        priority = d.pop("priority", UNSET)

        scope_reference = d.pop("scope_reference", UNSET)

        get_mission_action = cls(
            action_type=action_type,
            created_by_id=created_by_id,
            guid=guid,
            mission_id=mission_id,
            parameters=parameters,
            priority=priority,
            scope_reference=scope_reference,
        )

        get_mission_action.additional_properties = d
        return get_mission_action

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
