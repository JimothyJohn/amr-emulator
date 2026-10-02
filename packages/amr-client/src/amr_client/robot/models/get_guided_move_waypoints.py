from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetGuidedMoveWaypoints")


@_attrs_define
class GetGuidedMoveWaypoints:
    """
    Attributes:
        guided_move_id (str | Unset): The guided move id this guided move belongs to
        url (str | Unset): The URL of the resource
        waypoints (str | Unset):
    """

    guided_move_id: str | Unset = UNSET
    url: str | Unset = UNSET
    waypoints: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guided_move_id = self.guided_move_id

        url = self.url

        waypoints = self.waypoints

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guided_move_id is not UNSET:
            field_dict["guided_move_id"] = guided_move_id
        if url is not UNSET:
            field_dict["url"] = url
        if waypoints is not UNSET:
            field_dict["waypoints"] = waypoints

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guided_move_id = d.pop("guided_move_id", UNSET)

        url = d.pop("url", UNSET)

        waypoints = d.pop("waypoints", UNSET)

        get_guided_move_waypoints = cls(
            guided_move_id=guided_move_id,
            url=url,
            waypoints=waypoints,
        )

        get_guided_move_waypoints.additional_properties = d
        return get_guided_move_waypoints

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
