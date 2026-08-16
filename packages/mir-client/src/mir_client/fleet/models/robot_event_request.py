from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.robot_end_state import RobotEndState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.robot_state import RobotState


T = TypeVar("T", bound="RobotEventRequest")


@_attrs_define
class RobotEventRequest:
    """
    Attributes:
        robot_id (str | Unset):
        robot_state (RobotState | Unset):
        robot_end_state (RobotEndState | Unset):
        battery_percentage (float | Unset):
        uptime (str | Unset):
        battery_time_remaining_in_minutes (str | Unset):
        total_distance_moved_in_meters (float | Unset):
        pose_x (float | Unset):
        pose_y (float | Unset):
        pose_orientation (float | Unset):
        map_id (str | Unset):
        timestamp (datetime.datetime | Unset):
        battery_time_remaining (str | Unset):
        in_emergency_stop (bool | Unset):
    """

    robot_id: str | Unset = UNSET
    robot_state: RobotState | Unset = UNSET
    robot_end_state: RobotEndState | Unset = UNSET
    battery_percentage: float | Unset = UNSET
    uptime: str | Unset = UNSET
    battery_time_remaining_in_minutes: str | Unset = UNSET
    total_distance_moved_in_meters: float | Unset = UNSET
    pose_x: float | Unset = UNSET
    pose_y: float | Unset = UNSET
    pose_orientation: float | Unset = UNSET
    map_id: str | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    battery_time_remaining: str | Unset = UNSET
    in_emergency_stop: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        robot_id = self.robot_id

        robot_state: dict[str, Any] | Unset = UNSET
        if not isinstance(self.robot_state, Unset):
            robot_state = self.robot_state.to_dict()

        robot_end_state: str | Unset = UNSET
        if not isinstance(self.robot_end_state, Unset):
            robot_end_state = self.robot_end_state.value

        battery_percentage = self.battery_percentage

        uptime = self.uptime

        battery_time_remaining_in_minutes = self.battery_time_remaining_in_minutes

        total_distance_moved_in_meters = self.total_distance_moved_in_meters

        pose_x = self.pose_x

        pose_y = self.pose_y

        pose_orientation = self.pose_orientation

        map_id = self.map_id

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        battery_time_remaining = self.battery_time_remaining

        in_emergency_stop = self.in_emergency_stop

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id
        if robot_state is not UNSET:
            field_dict["robot-state"] = robot_state
        if robot_end_state is not UNSET:
            field_dict["robot-end-state"] = robot_end_state
        if battery_percentage is not UNSET:
            field_dict["battery-percentage"] = battery_percentage
        if uptime is not UNSET:
            field_dict["uptime"] = uptime
        if battery_time_remaining_in_minutes is not UNSET:
            field_dict["battery-time-remaining-in-minutes"] = battery_time_remaining_in_minutes
        if total_distance_moved_in_meters is not UNSET:
            field_dict["total-distance-moved-in-meters"] = total_distance_moved_in_meters
        if pose_x is not UNSET:
            field_dict["pose-x"] = pose_x
        if pose_y is not UNSET:
            field_dict["pose-y"] = pose_y
        if pose_orientation is not UNSET:
            field_dict["pose-orientation"] = pose_orientation
        if map_id is not UNSET:
            field_dict["map-id"] = map_id
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if battery_time_remaining is not UNSET:
            field_dict["battery-time-remaining"] = battery_time_remaining
        if in_emergency_stop is not UNSET:
            field_dict["in-emergency-stop"] = in_emergency_stop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.robot_state import RobotState

        d = dict(src_dict)
        robot_id = d.pop("robot-id", UNSET)

        _robot_state = d.pop("robot-state", UNSET)
        robot_state: RobotState | Unset
        if isinstance(_robot_state, Unset):
            robot_state = UNSET
        else:
            robot_state = RobotState.from_dict(_robot_state)

        _robot_end_state = d.pop("robot-end-state", UNSET)
        robot_end_state: RobotEndState | Unset
        if isinstance(_robot_end_state, Unset):
            robot_end_state = UNSET
        else:
            robot_end_state = RobotEndState(_robot_end_state)

        battery_percentage = d.pop("battery-percentage", UNSET)

        uptime = d.pop("uptime", UNSET)

        battery_time_remaining_in_minutes = d.pop("battery-time-remaining-in-minutes", UNSET)

        total_distance_moved_in_meters = d.pop("total-distance-moved-in-meters", UNSET)

        pose_x = d.pop("pose-x", UNSET)

        pose_y = d.pop("pose-y", UNSET)

        pose_orientation = d.pop("pose-orientation", UNSET)

        map_id = d.pop("map-id", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        battery_time_remaining = d.pop("battery-time-remaining", UNSET)

        in_emergency_stop = d.pop("in-emergency-stop", UNSET)

        robot_event_request = cls(
            robot_id=robot_id,
            robot_state=robot_state,
            robot_end_state=robot_end_state,
            battery_percentage=battery_percentage,
            uptime=uptime,
            battery_time_remaining_in_minutes=battery_time_remaining_in_minutes,
            total_distance_moved_in_meters=total_distance_moved_in_meters,
            pose_x=pose_x,
            pose_y=pose_y,
            pose_orientation=pose_orientation,
            map_id=map_id,
            timestamp=timestamp,
            battery_time_remaining=battery_time_remaining,
            in_emergency_stop=in_emergency_stop,
        )

        return robot_event_request
