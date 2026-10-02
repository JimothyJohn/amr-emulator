from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutGuidedMove")


@_attrs_define
class PutGuidedMove:
    """
    Attributes:
        assigned_waypoint_index (int | Unset): The waypoint index the robot is allowed to drive to
        guided_move_id (str | Unset): The action ID this guided move belongs to
    """

    assigned_waypoint_index: int | Unset = UNSET
    guided_move_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assigned_waypoint_index = self.assigned_waypoint_index

        guided_move_id = self.guided_move_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assigned_waypoint_index is not UNSET:
            field_dict["assigned_waypoint_index"] = assigned_waypoint_index
        if guided_move_id is not UNSET:
            field_dict["guided_move_id"] = guided_move_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assigned_waypoint_index = d.pop("assigned_waypoint_index", UNSET)

        guided_move_id = d.pop("guided_move_id", UNSET)

        put_guided_move = cls(
            assigned_waypoint_index=assigned_waypoint_index,
            guided_move_id=guided_move_id,
        )

        put_guided_move.additional_properties = d
        return put_guided_move

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
