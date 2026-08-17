from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.event_type_with_endpoints import EventTypeWithEndpoints


T = TypeVar("T", bound="SubscriptionResponse")


@_attrs_define
class SubscriptionResponse:
    """
    Attributes:
        base_url (str):
        endpoints (list[EventTypeWithEndpoints]):
    """

    base_url: str
    endpoints: list[EventTypeWithEndpoints]

    def to_dict(self) -> dict[str, Any]:
        base_url = self.base_url

        endpoints = []
        for endpoints_item_data in self.endpoints:
            endpoints_item = endpoints_item_data.to_dict()
            endpoints.append(endpoints_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "base-url": base_url,
                "endpoints": endpoints,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_type_with_endpoints import EventTypeWithEndpoints

        d = dict(src_dict)
        base_url = d.pop("base-url")

        endpoints = []
        _endpoints = d.pop("endpoints")
        for endpoints_item_data in _endpoints:
            endpoints_item = EventTypeWithEndpoints.from_dict(endpoints_item_data)

            endpoints.append(endpoints_item)

        subscription_response = cls(
            base_url=base_url,
            endpoints=endpoints,
        )

        return subscription_response
