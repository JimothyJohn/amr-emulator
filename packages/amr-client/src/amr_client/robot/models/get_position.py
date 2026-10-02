from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPosition")


@_attrs_define
class GetPosition:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        docking_offsets (str | Unset): The url to the possible docking offset. if the position does not have a docking
            offset then this field is empty
        guid (str | Unset): The global id unique across robots that identifies this position
        help_positions (str | Unset):
        map_ (str | Unset): The url to the map this position belongs to
        map_id (str | Unset): The global id of the map this positions belongs to
        name (str | Unset): The name of the position
        orientation (float | Unset): The orientation of the position in degrees relative to origo of the underlying map
        parent (str | Unset): The url to the possible parent position. if the position does not have a parent position
            then this field is empty
        parent_id (str | Unset): The global id of the possible parent position of the current position. a parent
            position is a position related to the current position, for instance the parent position of a trolley left entry
            position is the actual trolley position. if the position does not have a parent position then this field is
            empty
        pos_x (float | Unset): The x-coordinate of the position relative to origo of the underlying map
        pos_y (float | Unset): The y-coordinate of the position relative to origo of the underlying map
        type_ (str | Unset): The url to the description of the type of this position
        type_id (int | Unset): The type of position. see the general description above
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    docking_offsets: str | Unset = UNSET
    guid: str | Unset = UNSET
    help_positions: str | Unset = UNSET
    map_: str | Unset = UNSET
    map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    orientation: float | Unset = UNSET
    parent: str | Unset = UNSET
    parent_id: str | Unset = UNSET
    pos_x: float | Unset = UNSET
    pos_y: float | Unset = UNSET
    type_: str | Unset = UNSET
    type_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        docking_offsets = self.docking_offsets

        guid = self.guid

        help_positions = self.help_positions

        map_ = self.map_

        map_id = self.map_id

        name = self.name

        orientation = self.orientation

        parent = self.parent

        parent_id = self.parent_id

        pos_x = self.pos_x

        pos_y = self.pos_y

        type_ = self.type_

        type_id = self.type_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if docking_offsets is not UNSET:
            field_dict["docking_offsets"] = docking_offsets
        if guid is not UNSET:
            field_dict["guid"] = guid
        if help_positions is not UNSET:
            field_dict["help_positions"] = help_positions
        if map_ is not UNSET:
            field_dict["map"] = map_
        if map_id is not UNSET:
            field_dict["map_id"] = map_id
        if name is not UNSET:
            field_dict["name"] = name
        if orientation is not UNSET:
            field_dict["orientation"] = orientation
        if parent is not UNSET:
            field_dict["parent"] = parent
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if pos_x is not UNSET:
            field_dict["pos_x"] = pos_x
        if pos_y is not UNSET:
            field_dict["pos_y"] = pos_y
        if type_ is not UNSET:
            field_dict["type"] = type_
        if type_id is not UNSET:
            field_dict["type_id"] = type_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        docking_offsets = d.pop("docking_offsets", UNSET)

        guid = d.pop("guid", UNSET)

        help_positions = d.pop("help_positions", UNSET)

        map_ = d.pop("map", UNSET)

        map_id = d.pop("map_id", UNSET)

        name = d.pop("name", UNSET)

        orientation = d.pop("orientation", UNSET)

        parent = d.pop("parent", UNSET)

        parent_id = d.pop("parent_id", UNSET)

        pos_x = d.pop("pos_x", UNSET)

        pos_y = d.pop("pos_y", UNSET)

        type_ = d.pop("type", UNSET)

        type_id = d.pop("type_id", UNSET)

        get_position = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            docking_offsets=docking_offsets,
            guid=guid,
            help_positions=help_positions,
            map_=map_,
            map_id=map_id,
            name=name,
            orientation=orientation,
            parent=parent,
            parent_id=parent_id,
            pos_x=pos_x,
            pos_y=pos_y,
            type_=type_,
            type_id=type_id,
        )

        get_position.additional_properties = d
        return get_position

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
