from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="EventTypeWithEndpoints1")


@_attrs_define
class EventTypeWithEndpoints1:
    """
    Attributes:
        event_type (str | Unset):
        endpoint_paths (list[str] | Unset):
    """

    event_type: str | Unset = UNSET
    endpoint_paths: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        event_type = self.event_type

        endpoint_paths: list[str] | Unset = UNSET
        if not isinstance(self.endpoint_paths, Unset):
            endpoint_paths = self.endpoint_paths

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if event_type is not UNSET:
            field_dict["event-type"] = event_type
        if endpoint_paths is not UNSET:
            field_dict["endpoint-paths"] = endpoint_paths

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        event_type = d.pop("event-type", UNSET)

        endpoint_paths = cast(list[str], d.pop("endpoint-paths", UNSET))

        event_type_with_endpoints_1 = cls(
            event_type=event_type,
            endpoint_paths=endpoint_paths,
        )

        return event_type_with_endpoints_1
