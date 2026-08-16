from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMissionQueue")


@_attrs_define
class GetMissionQueue:
    """
    Attributes:
        actions (str | Unset): The list of parameters this mission queue entry accepts
        control_posid (str | Unset): Global id of position used during control states
        control_state (int | Unset): Mission control state. a value above zero indicates that the robot needs an
            external input in order to continue
        created_by (str | Unset): The url to the description of the type of this element
        created_by_id (str | Unset): The global id of the user who created this entry
        description (str | Unset): Inerited from mission description, when item was queued
        finished (datetime.datetime | Unset): The date and time when the mission was finished
        fleet_schedule_guid (str | Unset): The guid of the mission scheduler element this mission queue element
            corresponds to on the fleet
        id (int | Unset): The id of the mission queue entry
        message (str | Unset): The last message produced by the actions in the mission list
        mission (str | Unset): The url to the mission that mission that was executed
        mission_id (str | Unset): The global id of the mission that was executed
        ordered (datetime.datetime | Unset): The date end time when the mission was queued
        parameters (str | Unset):
        priority (int | Unset): The id of the action
        started (datetime.datetime | Unset): The date and time when the missin was started
        state (str | Unset): The end state after the mission was executed
    """

    actions: str | Unset = UNSET
    control_posid: str | Unset = UNSET
    control_state: int | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    description: str | Unset = UNSET
    finished: datetime.datetime | Unset = UNSET
    fleet_schedule_guid: str | Unset = UNSET
    id: int | Unset = UNSET
    message: str | Unset = UNSET
    mission: str | Unset = UNSET
    mission_id: str | Unset = UNSET
    ordered: datetime.datetime | Unset = UNSET
    parameters: str | Unset = UNSET
    priority: int | Unset = UNSET
    started: datetime.datetime | Unset = UNSET
    state: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions = self.actions

        control_posid = self.control_posid

        control_state = self.control_state

        created_by = self.created_by

        created_by_id = self.created_by_id

        description = self.description

        finished: str | Unset = UNSET
        if not isinstance(self.finished, Unset):
            finished = self.finished.isoformat()

        fleet_schedule_guid = self.fleet_schedule_guid

        id = self.id

        message = self.message

        mission = self.mission

        mission_id = self.mission_id

        ordered: str | Unset = UNSET
        if not isinstance(self.ordered, Unset):
            ordered = self.ordered.isoformat()

        parameters = self.parameters

        priority = self.priority

        started: str | Unset = UNSET
        if not isinstance(self.started, Unset):
            started = self.started.isoformat()

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if control_posid is not UNSET:
            field_dict["control_posid"] = control_posid
        if control_state is not UNSET:
            field_dict["control_state"] = control_state
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if description is not UNSET:
            field_dict["description"] = description
        if finished is not UNSET:
            field_dict["finished"] = finished
        if fleet_schedule_guid is not UNSET:
            field_dict["fleet_schedule_guid"] = fleet_schedule_guid
        if id is not UNSET:
            field_dict["id"] = id
        if message is not UNSET:
            field_dict["message"] = message
        if mission is not UNSET:
            field_dict["mission"] = mission
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if ordered is not UNSET:
            field_dict["ordered"] = ordered
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if priority is not UNSET:
            field_dict["priority"] = priority
        if started is not UNSET:
            field_dict["started"] = started
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        actions = d.pop("actions", UNSET)

        control_posid = d.pop("control_posid", UNSET)

        control_state = d.pop("control_state", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        description = d.pop("description", UNSET)

        _finished = d.pop("finished", UNSET)
        finished: datetime.datetime | Unset
        if isinstance(_finished, Unset):
            finished = UNSET
        else:
            finished = datetime.datetime.fromisoformat(_finished)

        fleet_schedule_guid = d.pop("fleet_schedule_guid", UNSET)

        id = d.pop("id", UNSET)

        message = d.pop("message", UNSET)

        mission = d.pop("mission", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        _ordered = d.pop("ordered", UNSET)
        ordered: datetime.datetime | Unset
        if isinstance(_ordered, Unset):
            ordered = UNSET
        else:
            ordered = datetime.datetime.fromisoformat(_ordered)

        parameters = d.pop("parameters", UNSET)

        priority = d.pop("priority", UNSET)

        _started = d.pop("started", UNSET)
        started: datetime.datetime | Unset
        if isinstance(_started, Unset):
            started = UNSET
        else:
            started = datetime.datetime.fromisoformat(_started)

        state = d.pop("state", UNSET)

        get_mission_queue = cls(
            actions=actions,
            control_posid=control_posid,
            control_state=control_state,
            created_by=created_by,
            created_by_id=created_by_id,
            description=description,
            finished=finished,
            fleet_schedule_guid=fleet_schedule_guid,
            id=id,
            message=message,
            mission=mission,
            mission_id=mission_id,
            ordered=ordered,
            parameters=parameters,
            priority=priority,
            started=started,
            state=state,
        )

        get_mission_queue.additional_properties = d
        return get_mission_queue

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
