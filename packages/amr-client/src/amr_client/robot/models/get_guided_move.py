from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetGuidedMove")


@_attrs_define
class GetGuidedMove:
    """
    Attributes:
        assigned_waypoint_index (int | Unset): The waypoint index the robot is allowed to drive to
        current_waypoint_index (int | Unset): The current waypoint index the robot is at
        guided_move_id (str | Unset): The guided move id this guided move belongs to
        node_resource_handling_enabled (str | Unset): Whether node resource handling is enabled for this guided move
        url (str | Unset): The URL of the resource
    """

    assigned_waypoint_index: int | Unset = UNSET
    current_waypoint_index: int | Unset = UNSET
    guided_move_id: str | Unset = UNSET
    node_resource_handling_enabled: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assigned_waypoint_index = self.assigned_waypoint_index

        current_waypoint_index = self.current_waypoint_index

        guided_move_id = self.guided_move_id

        node_resource_handling_enabled = self.node_resource_handling_enabled

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assigned_waypoint_index is not UNSET:
            field_dict["assigned_waypoint_index"] = assigned_waypoint_index
        if current_waypoint_index is not UNSET:
            field_dict["current_waypoint_index"] = current_waypoint_index
        if guided_move_id is not UNSET:
            field_dict["guided_move_id"] = guided_move_id
        if node_resource_handling_enabled is not UNSET:
            field_dict["node_resource_handling_enabled"] = node_resource_handling_enabled
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assigned_waypoint_index = d.pop("assigned_waypoint_index", UNSET)

        current_waypoint_index = d.pop("current_waypoint_index", UNSET)

        guided_move_id = d.pop("guided_move_id", UNSET)

        node_resource_handling_enabled = d.pop("node_resource_handling_enabled", UNSET)

        url = d.pop("url", UNSET)

        get_guided_move = cls(
            assigned_waypoint_index=assigned_waypoint_index,
            current_waypoint_index=current_waypoint_index,
            guided_move_id=guided_move_id,
            node_resource_handling_enabled=node_resource_handling_enabled,
            url=url,
        )

        get_guided_move.additional_properties = d
        return get_guided_move

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
