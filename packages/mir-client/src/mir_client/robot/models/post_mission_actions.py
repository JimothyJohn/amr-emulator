from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_mission_actions_parameters_item import PostMissionActionsParametersItem


T = TypeVar("T", bound="PostMissionActions")


@_attrs_define
class PostMissionActions:
    """
    Attributes:
        action_type (str): Min length: 1, Max length: 255
        mission_id (str):
        parameters (list[PostMissionActionsParametersItem]):
        priority (int):
        guid (str | Unset):
        scope_reference (str | Unset):
    """

    action_type: str
    mission_id: str
    parameters: list[PostMissionActionsParametersItem]
    priority: int
    guid: str | Unset = UNSET
    scope_reference: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_type = self.action_type

        mission_id = self.mission_id

        parameters = []
        for parameters_item_data in self.parameters:
            parameters_item = parameters_item_data.to_dict()
            parameters.append(parameters_item)

        priority = self.priority

        guid = self.guid

        scope_reference = self.scope_reference

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action_type": action_type,
                "mission_id": mission_id,
                "parameters": parameters,
                "priority": priority,
            }
        )
        if guid is not UNSET:
            field_dict["guid"] = guid
        if scope_reference is not UNSET:
            field_dict["scope_reference"] = scope_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_mission_actions_parameters_item import PostMissionActionsParametersItem

        d = dict(src_dict)
        action_type = d.pop("action_type")

        mission_id = d.pop("mission_id")

        parameters = []
        _parameters = d.pop("parameters")
        for parameters_item_data in _parameters:
            parameters_item = PostMissionActionsParametersItem.from_dict(parameters_item_data)

            parameters.append(parameters_item)

        priority = d.pop("priority")

        guid = d.pop("guid", UNSET)

        scope_reference = d.pop("scope_reference", UNSET)

        post_mission_actions = cls(
            action_type=action_type,
            mission_id=mission_id,
            parameters=parameters,
            priority=priority,
            guid=guid,
            scope_reference=scope_reference,
        )

        post_mission_actions.additional_properties = d
        return post_mission_actions

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
