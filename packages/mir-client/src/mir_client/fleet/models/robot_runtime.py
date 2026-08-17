from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hook_data import HookData
    from ..models.pose import Pose


T = TypeVar("T", bound="RobotRuntime")


@_attrs_define
class RobotRuntime:
    """
    Attributes:
        uptime (str):
        battery_percentage (float):
        battery_time_remaining (str):
        pose (Pose):
        velocity_linear (float):
        velocity_angular (float):
        moved (float):
        timestamp (datetime.datetime):
        hook_data (HookData | Unset):
    """

    uptime: str
    battery_percentage: float
    battery_time_remaining: str
    pose: Pose
    velocity_linear: float
    velocity_angular: float
    moved: float
    timestamp: datetime.datetime
    hook_data: HookData | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        uptime = self.uptime

        battery_percentage = self.battery_percentage

        battery_time_remaining = self.battery_time_remaining

        pose = self.pose.to_dict()

        velocity_linear = self.velocity_linear

        velocity_angular = self.velocity_angular

        moved = self.moved

        timestamp = self.timestamp.isoformat()

        hook_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hook_data, Unset):
            hook_data = self.hook_data.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "uptime": uptime,
                "battery-percentage": battery_percentage,
                "battery-time-remaining": battery_time_remaining,
                "pose": pose,
                "velocity-linear": velocity_linear,
                "velocity-angular": velocity_angular,
                "moved": moved,
                "timestamp": timestamp,
            }
        )
        if hook_data is not UNSET:
            field_dict["hook-data"] = hook_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.hook_data import HookData
        from ..models.pose import Pose

        d = dict(src_dict)
        uptime = d.pop("uptime")

        battery_percentage = d.pop("battery-percentage")

        battery_time_remaining = d.pop("battery-time-remaining")

        pose = Pose.from_dict(d.pop("pose"))

        velocity_linear = d.pop("velocity-linear")

        velocity_angular = d.pop("velocity-angular")

        moved = d.pop("moved")

        timestamp = datetime.datetime.fromisoformat(d.pop("timestamp"))

        _hook_data = d.pop("hook-data", UNSET)
        hook_data: HookData | Unset
        if isinstance(_hook_data, Unset):
            hook_data = UNSET
        else:
            hook_data = HookData.from_dict(_hook_data)

        robot_runtime = cls(
            uptime=uptime,
            battery_percentage=battery_percentage,
            battery_time_remaining=battery_time_remaining,
            pose=pose,
            velocity_linear=velocity_linear,
            velocity_angular=velocity_angular,
            moved=moved,
            timestamp=timestamp,
            hook_data=hook_data,
        )

        return robot_runtime
