from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutPosition")


@_attrs_define
class PutPosition:
    """
    Attributes:
        map_id (str | Unset):
        name (str | Unset): Min length: 1, Max length: 40
        orientation (float | Unset):
        parent_id (str | Unset):
        pos_x (float | Unset):
        pos_y (float | Unset):
        type_id (int | Unset):
    """

    map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    orientation: float | Unset = UNSET
    parent_id: str | Unset = UNSET
    pos_x: float | Unset = UNSET
    pos_y: float | Unset = UNSET
    type_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        map_id = self.map_id

        name = self.name

        orientation = self.orientation

        parent_id = self.parent_id

        pos_x = self.pos_x

        pos_y = self.pos_y

        type_id = self.type_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if map_id is not UNSET:
            field_dict["map_id"] = map_id
        if name is not UNSET:
            field_dict["name"] = name
        if orientation is not UNSET:
            field_dict["orientation"] = orientation
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if pos_x is not UNSET:
            field_dict["pos_x"] = pos_x
        if pos_y is not UNSET:
            field_dict["pos_y"] = pos_y
        if type_id is not UNSET:
            field_dict["type_id"] = type_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        map_id = d.pop("map_id", UNSET)

        name = d.pop("name", UNSET)

        orientation = d.pop("orientation", UNSET)

        parent_id = d.pop("parent_id", UNSET)

        pos_x = d.pop("pos_x", UNSET)

        pos_y = d.pop("pos_y", UNSET)

        type_id = d.pop("type_id", UNSET)

        put_position = cls(
            map_id=map_id,
            name=name,
            orientation=orientation,
            parent_id=parent_id,
            pos_x=pos_x,
            pos_y=pos_y,
            type_id=type_id,
        )

        put_position.additional_properties = d
        return put_position

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
