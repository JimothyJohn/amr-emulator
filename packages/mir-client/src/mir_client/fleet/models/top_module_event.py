from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.top_module_event_payload import TopModuleEventPayload


T = TypeVar("T", bound="TopModuleEvent")


@_attrs_define
class TopModuleEvent:
    """
    Attributes:
        name (str):
        payload (TopModuleEventPayload):
    """

    name: str
    payload: TopModuleEventPayload

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "payload": payload,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.top_module_event_payload import TopModuleEventPayload

        d = dict(src_dict)
        name = d.pop("name")

        payload = TopModuleEventPayload.from_dict(d.pop("payload"))

        top_module_event = cls(
            name=name,
            payload=payload,
        )

        return top_module_event
