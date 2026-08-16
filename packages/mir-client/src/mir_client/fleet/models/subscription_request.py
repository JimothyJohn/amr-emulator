from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_type_with_endpoints import EventTypeWithEndpoints


T = TypeVar("T", bound="SubscriptionRequest")


@_attrs_define
class SubscriptionRequest:
    """
    Attributes:
        base_url (str):
        endpoints (list[EventTypeWithEndpoints]):
        access_token (None | str | Unset):
        max_retries (int | None | Unset):
        ignore_certificate_errors (bool | Unset):
    """

    base_url: str
    endpoints: list[EventTypeWithEndpoints]
    access_token: None | str | Unset = UNSET
    max_retries: int | None | Unset = UNSET
    ignore_certificate_errors: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        base_url = self.base_url

        endpoints = []
        for endpoints_item_data in self.endpoints:
            endpoints_item = endpoints_item_data.to_dict()
            endpoints.append(endpoints_item)

        access_token: None | str | Unset
        if isinstance(self.access_token, Unset):
            access_token = UNSET
        else:
            access_token = self.access_token

        max_retries: int | None | Unset
        if isinstance(self.max_retries, Unset):
            max_retries = UNSET
        else:
            max_retries = self.max_retries

        ignore_certificate_errors = self.ignore_certificate_errors

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "base-url": base_url,
                "endpoints": endpoints,
            }
        )
        if access_token is not UNSET:
            field_dict["access-token"] = access_token
        if max_retries is not UNSET:
            field_dict["max-retries"] = max_retries
        if ignore_certificate_errors is not UNSET:
            field_dict["ignore-certificate-errors"] = ignore_certificate_errors

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

        def _parse_access_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        access_token = _parse_access_token(d.pop("access-token", UNSET))

        def _parse_max_retries(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_retries = _parse_max_retries(d.pop("max-retries", UNSET))

        ignore_certificate_errors = d.pop("ignore-certificate-errors", UNSET)

        subscription_request = cls(
            base_url=base_url,
            endpoints=endpoints,
            access_token=access_token,
            max_retries=max_retries,
            ignore_certificate_errors=ignore_certificate_errors,
        )

        return subscription_request
