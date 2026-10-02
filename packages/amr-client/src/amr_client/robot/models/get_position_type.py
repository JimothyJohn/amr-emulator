from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPositionType")


@_attrs_define
class GetPositionType:
    """
    Attributes:
        hidden (bool | Unset): False if the position is not created by the user
        id (int | Unset): Unique id for the position type
        name (str | Unset): Name of the position type
        reachable_for_robot (bool | Unset): True if the robot can actually go to that position
    """

    hidden: bool | Unset = UNSET
    id: int | Unset = UNSET
    name: str | Unset = UNSET
    reachable_for_robot: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hidden = self.hidden

        id = self.id

        name = self.name

        reachable_for_robot = self.reachable_for_robot

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hidden is not UNSET:
            field_dict["hidden"] = hidden
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if reachable_for_robot is not UNSET:
            field_dict["reachable_for_robot"] = reachable_for_robot

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hidden = d.pop("hidden", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        reachable_for_robot = d.pop("reachable_for_robot", UNSET)

        get_position_type = cls(
            hidden=hidden,
            id=id,
            name=name,
            reachable_for_robot=reachable_for_robot,
        )

        get_position_type.additional_properties = d
        return get_position_type

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
