from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMissionActions")


@_attrs_define
class GetMissionActions:
    """
    Attributes:
        action_type (str | Unset): The id of the type of action
        guid (str | Unset): The global id unique across robots that identifies this mission
        mission_id (str | Unset): The id of the mission the action belongs to
        parameters (str | Unset):
        priority (int | Unset): The priority of the action
        url (str | Unset): The URL of the resource
    """

    action_type: str | Unset = UNSET
    guid: str | Unset = UNSET
    mission_id: str | Unset = UNSET
    parameters: str | Unset = UNSET
    priority: int | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_type = self.action_type

        guid = self.guid

        mission_id = self.mission_id

        parameters = self.parameters

        priority = self.priority

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_type is not UNSET:
            field_dict["action_type"] = action_type
        if guid is not UNSET:
            field_dict["guid"] = guid
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if priority is not UNSET:
            field_dict["priority"] = priority
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action_type = d.pop("action_type", UNSET)

        guid = d.pop("guid", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        parameters = d.pop("parameters", UNSET)

        priority = d.pop("priority", UNSET)

        url = d.pop("url", UNSET)

        get_mission_actions = cls(
            action_type=action_type,
            guid=guid,
            mission_id=mission_id,
            parameters=parameters,
            priority=priority,
            url=url,
        )

        get_mission_actions.additional_properties = d
        return get_mission_actions

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
