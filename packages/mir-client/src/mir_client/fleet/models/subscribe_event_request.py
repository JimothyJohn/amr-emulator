from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.subscription_state import SubscriptionState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_type_with_endpoints_1 import EventTypeWithEndpoints1


T = TypeVar("T", bound="SubscribeEventRequest")


@_attrs_define
class SubscribeEventRequest:
    """
    Attributes:
        base_url (str | Unset):
        endpoints (list[EventTypeWithEndpoints1] | Unset):
        state (SubscriptionState | Unset):
        timestamp (datetime.datetime | Unset):
    """

    base_url: str | Unset = UNSET
    endpoints: list[EventTypeWithEndpoints1] | Unset = UNSET
    state: SubscriptionState | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        base_url = self.base_url

        endpoints: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.endpoints, Unset):
            endpoints = []
            for endpoints_item_data in self.endpoints:
                endpoints_item = endpoints_item_data.to_dict()
                endpoints.append(endpoints_item)

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if base_url is not UNSET:
            field_dict["base-url"] = base_url
        if endpoints is not UNSET:
            field_dict["endpoints"] = endpoints
        if state is not UNSET:
            field_dict["state"] = state
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_type_with_endpoints_1 import EventTypeWithEndpoints1

        d = dict(src_dict)
        base_url = d.pop("base-url", UNSET)

        _endpoints = d.pop("endpoints", UNSET)
        endpoints: list[EventTypeWithEndpoints1] | Unset = UNSET
        if _endpoints is not UNSET:
            endpoints = []
            for endpoints_item_data in _endpoints:
                endpoints_item = EventTypeWithEndpoints1.from_dict(endpoints_item_data)

                endpoints.append(endpoints_item)

        _state = d.pop("state", UNSET)
        state: SubscriptionState | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = SubscriptionState(_state)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        subscribe_event_request = cls(
            base_url=base_url,
            endpoints=endpoints,
            state=state,
            timestamp=timestamp,
        )

        return subscribe_event_request
