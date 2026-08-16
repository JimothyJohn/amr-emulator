from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.top_module_event import TopModuleEvent


T = TypeVar("T", bound="TopModuleEventRequest1")


@_attrs_define
class TopModuleEventRequest1:
    """
    Attributes:
        robot_id (str):
        event (TopModuleEvent):
    """

    robot_id: str
    event: TopModuleEvent

    def to_dict(self) -> dict[str, Any]:
        robot_id = self.robot_id

        event = self.event.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "robot-id": robot_id,
                "event": event,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.top_module_event import TopModuleEvent

        d = dict(src_dict)
        robot_id = d.pop("robot-id")

        event = TopModuleEvent.from_dict(d.pop("event"))

        top_module_event_request_1 = cls(
            robot_id=robot_id,
            event=event,
        )

        return top_module_event_request_1
