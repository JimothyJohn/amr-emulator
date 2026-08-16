from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_mission_queue_actions_parameters_item import (
        GetMissionQueueActionsParametersItem,
    )


T = TypeVar("T", bound="GetMissionQueueActions")


@_attrs_define
class GetMissionQueueActions:
    """
    Attributes:
        action_id (str | Unset): The id of the action
        action_type (str | Unset): The name of the action
        finished (datetime.datetime | Unset): The date and time when the action finished
        id (int | Unset): The id of the action
        message (str | Unset): The possible message produced by the action
        mission_queue_id (int | Unset): The id of the action
        parameters (list[GetMissionQueueActionsParametersItem] | Unset): The list of parameters to the action
        started (datetime.datetime | Unset): The date and time when the action was started
        state (str | Unset): The end state after executing the action
    """

    action_id: str | Unset = UNSET
    action_type: str | Unset = UNSET
    finished: datetime.datetime | Unset = UNSET
    id: int | Unset = UNSET
    message: str | Unset = UNSET
    mission_queue_id: int | Unset = UNSET
    parameters: list[GetMissionQueueActionsParametersItem] | Unset = UNSET
    started: datetime.datetime | Unset = UNSET
    state: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_id = self.action_id

        action_type = self.action_type

        finished: str | Unset = UNSET
        if not isinstance(self.finished, Unset):
            finished = self.finished.isoformat()

        id = self.id

        message = self.message

        mission_queue_id = self.mission_queue_id

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)

        started: str | Unset = UNSET
        if not isinstance(self.started, Unset):
            started = self.started.isoformat()

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_id is not UNSET:
            field_dict["action_id"] = action_id
        if action_type is not UNSET:
            field_dict["action_type"] = action_type
        if finished is not UNSET:
            field_dict["finished"] = finished
        if id is not UNSET:
            field_dict["id"] = id
        if message is not UNSET:
            field_dict["message"] = message
        if mission_queue_id is not UNSET:
            field_dict["mission_queue_id"] = mission_queue_id
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if started is not UNSET:
            field_dict["started"] = started
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_mission_queue_actions_parameters_item import (
            GetMissionQueueActionsParametersItem,
        )

        d = dict(src_dict)
        action_id = d.pop("action_id", UNSET)

        action_type = d.pop("action_type", UNSET)

        _finished = d.pop("finished", UNSET)
        finished: datetime.datetime | Unset
        if isinstance(_finished, Unset):
            finished = UNSET
        else:
            finished = datetime.datetime.fromisoformat(_finished)

        id = d.pop("id", UNSET)

        message = d.pop("message", UNSET)

        mission_queue_id = d.pop("mission_queue_id", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: list[GetMissionQueueActionsParametersItem] | Unset = UNSET
        if _parameters is not UNSET:
            parameters = []
            for parameters_item_data in _parameters:
                parameters_item = GetMissionQueueActionsParametersItem.from_dict(
                    parameters_item_data
                )

                parameters.append(parameters_item)

        _started = d.pop("started", UNSET)
        started: datetime.datetime | Unset
        if isinstance(_started, Unset):
            started = UNSET
        else:
            started = datetime.datetime.fromisoformat(_started)

        state = d.pop("state", UNSET)

        get_mission_queue_actions = cls(
            action_id=action_id,
            action_type=action_type,
            finished=finished,
            id=id,
            message=message,
            mission_queue_id=mission_queue_id,
            parameters=parameters,
            started=started,
            state=state,
        )

        get_mission_queue_actions.additional_properties = d
        return get_mission_queue_actions

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
