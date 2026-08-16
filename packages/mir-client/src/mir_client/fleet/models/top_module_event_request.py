from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.top_module_event_type import TopModuleEventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error_1 import Error1
    from ..models.event import Event


T = TypeVar("T", bound="TopModuleEventRequest")


@_attrs_define
class TopModuleEventRequest:
    """
    Attributes:
        event_type (TopModuleEventType | Unset):
        event (Event | Unset):
        error (Error1 | Unset):
    """

    event_type: TopModuleEventType | Unset = UNSET
    event: Event | Unset = UNSET
    error: Error1 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        event_type: str | Unset = UNSET
        if not isinstance(self.event_type, Unset):
            event_type = self.event_type.value

        event: dict[str, Any] | Unset = UNSET
        if not isinstance(self.event, Unset):
            event = self.event.to_dict()

        error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if event_type is not UNSET:
            field_dict["event-type"] = event_type
        if event is not UNSET:
            field_dict["event"] = event
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_1 import Error1
        from ..models.event import Event

        d = dict(src_dict)
        _event_type = d.pop("event-type", UNSET)
        event_type: TopModuleEventType | Unset
        if isinstance(_event_type, Unset):
            event_type = UNSET
        else:
            event_type = TopModuleEventType(_event_type)

        _event = d.pop("event", UNSET)
        event: Event | Unset
        if isinstance(_event, Unset):
            event = UNSET
        else:
            event = Event.from_dict(_event)

        _error = d.pop("error", UNSET)
        error: Error1 | Unset
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = Error1.from_dict(_error)

        top_module_event_request = cls(
            event_type=event_type,
            event=event,
            error=error,
        )

        return top_module_event_request
