from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.subscription_event_type import SubscriptionEventType

T = TypeVar("T", bound="EventTypeWithEndpoints")


@_attrs_define
class EventTypeWithEndpoints:
    """
    Attributes:
        event_type (SubscriptionEventType):
        endpoint_paths (list[str]):
    """

    event_type: SubscriptionEventType
    endpoint_paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        event_type = self.event_type.value

        endpoint_paths = self.endpoint_paths

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "event-type": event_type,
                "endpoint-paths": endpoint_paths,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        event_type = SubscriptionEventType(d.pop("event-type"))

        endpoint_paths = cast(list[str], d.pop("endpoint-paths"))

        event_type_with_endpoints = cls(
            event_type=event_type,
            endpoint_paths=endpoint_paths,
        )

        return event_type_with_endpoints
