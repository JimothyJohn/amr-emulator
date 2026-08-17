from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_mission_queues_parameters_item import PostMissionQueuesParametersItem


T = TypeVar("T", bound="PostMissionQueues")


@_attrs_define
class PostMissionQueues:
    """
    Attributes:
        mission_id (str):
        description (str | Unset): Max length: 200
        fleet_schedule_guid (str | Unset): Max length: 36
        message (str | Unset): Max length: 200
        parameters (list[PostMissionQueuesParametersItem] | Unset):
        priority (int | Unset):
    """

    mission_id: str
    description: str | Unset = UNSET
    fleet_schedule_guid: str | Unset = UNSET
    message: str | Unset = UNSET
    parameters: list[PostMissionQueuesParametersItem] | Unset = UNSET
    priority: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mission_id = self.mission_id

        description = self.description

        fleet_schedule_guid = self.fleet_schedule_guid

        message = self.message

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mission_id": mission_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if fleet_schedule_guid is not UNSET:
            field_dict["fleet_schedule_guid"] = fleet_schedule_guid
        if message is not UNSET:
            field_dict["message"] = message
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_mission_queues_parameters_item import PostMissionQueuesParametersItem

        d = dict(src_dict)
        mission_id = d.pop("mission_id")

        description = d.pop("description", UNSET)

        fleet_schedule_guid = d.pop("fleet_schedule_guid", UNSET)

        message = d.pop("message", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: list[PostMissionQueuesParametersItem] | Unset = UNSET
        if _parameters is not UNSET:
            parameters = []
            for parameters_item_data in _parameters:
                parameters_item = PostMissionQueuesParametersItem.from_dict(parameters_item_data)

                parameters.append(parameters_item)

        priority = d.pop("priority", UNSET)

        post_mission_queues = cls(
            mission_id=mission_id,
            description=description,
            fleet_schedule_guid=fleet_schedule_guid,
            message=message,
            parameters=parameters,
            priority=priority,
        )

        post_mission_queues.additional_properties = d
        return post_mission_queues

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
