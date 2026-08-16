from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostPositions")


@_attrs_define
class PostPositions:
    """
    Attributes:
        map_id (str):
        name (str): Min length: 1, Max length: 40
        orientation (float):
        pos_x (float):
        pos_y (float):
        type_id (int):
        created_by_id (str | Unset):
        guid (str | Unset):
        parent_id (str | Unset):
    """

    map_id: str
    name: str
    orientation: float
    pos_x: float
    pos_y: float
    type_id: int
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    parent_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        map_id = self.map_id

        name = self.name

        orientation = self.orientation

        pos_x = self.pos_x

        pos_y = self.pos_y

        type_id = self.type_id

        created_by_id = self.created_by_id

        guid = self.guid

        parent_id = self.parent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "map_id": map_id,
                "name": name,
                "orientation": orientation,
                "pos_x": pos_x,
                "pos_y": pos_y,
                "type_id": type_id,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        map_id = d.pop("map_id")

        name = d.pop("name")

        orientation = d.pop("orientation")

        pos_x = d.pop("pos_x")

        pos_y = d.pop("pos_y")

        type_id = d.pop("type_id")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        parent_id = d.pop("parent_id", UNSET)

        post_positions = cls(
            map_id=map_id,
            name=name,
            orientation=orientation,
            pos_x=pos_x,
            pos_y=pos_y,
            type_id=type_id,
            created_by_id=created_by_id,
            guid=guid,
            parent_id=parent_id,
        )

        post_positions.additional_properties = d
        return post_positions

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
