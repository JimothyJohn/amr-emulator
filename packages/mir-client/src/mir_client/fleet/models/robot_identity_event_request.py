from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.robot_identity import RobotIdentity


T = TypeVar("T", bound="RobotIdentityEventRequest")


@_attrs_define
class RobotIdentityEventRequest:
    """
    Attributes:
        is_snapshot (bool | Unset):
        robot_identity_events (list[RobotIdentity] | Unset):
    """

    is_snapshot: bool | Unset = UNSET
    robot_identity_events: list[RobotIdentity] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_snapshot = self.is_snapshot

        robot_identity_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.robot_identity_events, Unset):
            robot_identity_events = []
            for robot_identity_events_item_data in self.robot_identity_events:
                robot_identity_events_item = robot_identity_events_item_data.to_dict()
                robot_identity_events.append(robot_identity_events_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_snapshot is not UNSET:
            field_dict["is-snapshot"] = is_snapshot
        if robot_identity_events is not UNSET:
            field_dict["robot-identity-events"] = robot_identity_events

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.robot_identity import RobotIdentity

        d = dict(src_dict)
        is_snapshot = d.pop("is-snapshot", UNSET)

        _robot_identity_events = d.pop("robot-identity-events", UNSET)
        robot_identity_events: list[RobotIdentity] | Unset = UNSET
        if _robot_identity_events is not UNSET:
            robot_identity_events = []
            for robot_identity_events_item_data in _robot_identity_events:
                robot_identity_events_item = RobotIdentity.from_dict(
                    robot_identity_events_item_data
                )

                robot_identity_events.append(robot_identity_events_item)

        robot_identity_event_request = cls(
            is_snapshot=is_snapshot,
            robot_identity_events=robot_identity_events,
        )

        return robot_identity_event_request
