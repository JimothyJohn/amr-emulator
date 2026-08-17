from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.obstacle_history_clearing import ObstacleHistoryClearing
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlannerZone")


@_attrs_define
class PlannerZone:
    """
    Attributes:
        disable_localisation (bool | Unset):
        look_ahead_distance (float | None | Unset):
        wait_for_obstacle_timeout (float | None | Unset):
        deviation_distance (float | None | Unset):
        ignore_camera_obstacle_data (bool | Unset):
        obstacle_history_clearing (ObstacleHistoryClearing | Unset):
    """

    disable_localisation: bool | Unset = UNSET
    look_ahead_distance: float | None | Unset = UNSET
    wait_for_obstacle_timeout: float | None | Unset = UNSET
    deviation_distance: float | None | Unset = UNSET
    ignore_camera_obstacle_data: bool | Unset = UNSET
    obstacle_history_clearing: ObstacleHistoryClearing | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        disable_localisation = self.disable_localisation

        look_ahead_distance: float | None | Unset
        if isinstance(self.look_ahead_distance, Unset):
            look_ahead_distance = UNSET
        else:
            look_ahead_distance = self.look_ahead_distance

        wait_for_obstacle_timeout: float | None | Unset
        if isinstance(self.wait_for_obstacle_timeout, Unset):
            wait_for_obstacle_timeout = UNSET
        else:
            wait_for_obstacle_timeout = self.wait_for_obstacle_timeout

        deviation_distance: float | None | Unset
        if isinstance(self.deviation_distance, Unset):
            deviation_distance = UNSET
        else:
            deviation_distance = self.deviation_distance

        ignore_camera_obstacle_data = self.ignore_camera_obstacle_data

        obstacle_history_clearing: str | Unset = UNSET
        if not isinstance(self.obstacle_history_clearing, Unset):
            obstacle_history_clearing = self.obstacle_history_clearing.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if disable_localisation is not UNSET:
            field_dict["disable-localisation"] = disable_localisation
        if look_ahead_distance is not UNSET:
            field_dict["look-ahead-distance"] = look_ahead_distance
        if wait_for_obstacle_timeout is not UNSET:
            field_dict["wait-for-obstacle-timeout"] = wait_for_obstacle_timeout
        if deviation_distance is not UNSET:
            field_dict["deviation-distance"] = deviation_distance
        if ignore_camera_obstacle_data is not UNSET:
            field_dict["ignore-camera-obstacle-data"] = ignore_camera_obstacle_data
        if obstacle_history_clearing is not UNSET:
            field_dict["obstacle-history-clearing"] = obstacle_history_clearing

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        disable_localisation = d.pop("disable-localisation", UNSET)

        def _parse_look_ahead_distance(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        look_ahead_distance = _parse_look_ahead_distance(d.pop("look-ahead-distance", UNSET))

        def _parse_wait_for_obstacle_timeout(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        wait_for_obstacle_timeout = _parse_wait_for_obstacle_timeout(
            d.pop("wait-for-obstacle-timeout", UNSET)
        )

        def _parse_deviation_distance(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        deviation_distance = _parse_deviation_distance(d.pop("deviation-distance", UNSET))

        ignore_camera_obstacle_data = d.pop("ignore-camera-obstacle-data", UNSET)

        _obstacle_history_clearing = d.pop("obstacle-history-clearing", UNSET)
        obstacle_history_clearing: ObstacleHistoryClearing | Unset
        if isinstance(_obstacle_history_clearing, Unset):
            obstacle_history_clearing = UNSET
        else:
            obstacle_history_clearing = ObstacleHistoryClearing(_obstacle_history_clearing)

        planner_zone = cls(
            disable_localisation=disable_localisation,
            look_ahead_distance=look_ahead_distance,
            wait_for_obstacle_timeout=wait_for_obstacle_timeout,
            deviation_distance=deviation_distance,
            ignore_camera_obstacle_data=ignore_camera_obstacle_data,
            obstacle_history_clearing=obstacle_history_clearing,
        )

        return planner_zone
