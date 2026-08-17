from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDockingOffset")


@_attrs_define
class GetDockingOffset:
    """
    Attributes:
        bar_distance (float | Unset): The width of the bars for bar_markers
        bar_length (float | Unset): The length of the bars for bar_markers
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        docking_type (int | Unset): The docking type of the marker.
        guid (str | Unset): The global id unique across robots that identifies this docking offset
        name (str | Unset): The name of the docking offset. used for docking offset independent from positions.
        orientation_offset (float | Unset): The orientation offset with respect to the docking marker
        pos_id (str | Unset): The global id refering to the position that this offset belongs to
        position (str | Unset): The url to the position
        shelf_leg_asymmetry_x (float | Unset): The asymmetry of the shelf legs in the x direction with respect to the
            shelf legs marker
        x_offset (float | Unset): The x-offset with respect to the docking marker
        y_offset (float | Unset): The y-offset with respect to the docking marker
    """

    bar_distance: float | Unset = UNSET
    bar_length: float | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    docking_type: int | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    orientation_offset: float | Unset = UNSET
    pos_id: str | Unset = UNSET
    position: str | Unset = UNSET
    shelf_leg_asymmetry_x: float | Unset = UNSET
    x_offset: float | Unset = UNSET
    y_offset: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bar_distance = self.bar_distance

        bar_length = self.bar_length

        created_by = self.created_by

        created_by_id = self.created_by_id

        docking_type = self.docking_type

        guid = self.guid

        name = self.name

        orientation_offset = self.orientation_offset

        pos_id = self.pos_id

        position = self.position

        shelf_leg_asymmetry_x = self.shelf_leg_asymmetry_x

        x_offset = self.x_offset

        y_offset = self.y_offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bar_distance is not UNSET:
            field_dict["bar_distance"] = bar_distance
        if bar_length is not UNSET:
            field_dict["bar_length"] = bar_length
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if docking_type is not UNSET:
            field_dict["docking_type"] = docking_type
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if orientation_offset is not UNSET:
            field_dict["orientation_offset"] = orientation_offset
        if pos_id is not UNSET:
            field_dict["pos_id"] = pos_id
        if position is not UNSET:
            field_dict["position"] = position
        if shelf_leg_asymmetry_x is not UNSET:
            field_dict["shelf_leg_asymmetry_x"] = shelf_leg_asymmetry_x
        if x_offset is not UNSET:
            field_dict["x_offset"] = x_offset
        if y_offset is not UNSET:
            field_dict["y_offset"] = y_offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bar_distance = d.pop("bar_distance", UNSET)

        bar_length = d.pop("bar_length", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        docking_type = d.pop("docking_type", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        orientation_offset = d.pop("orientation_offset", UNSET)

        pos_id = d.pop("pos_id", UNSET)

        position = d.pop("position", UNSET)

        shelf_leg_asymmetry_x = d.pop("shelf_leg_asymmetry_x", UNSET)

        x_offset = d.pop("x_offset", UNSET)

        y_offset = d.pop("y_offset", UNSET)

        get_docking_offset = cls(
            bar_distance=bar_distance,
            bar_length=bar_length,
            created_by=created_by,
            created_by_id=created_by_id,
            docking_type=docking_type,
            guid=guid,
            name=name,
            orientation_offset=orientation_offset,
            pos_id=pos_id,
            position=position,
            shelf_leg_asymmetry_x=shelf_leg_asymmetry_x,
            x_offset=x_offset,
            y_offset=y_offset,
        )

        get_docking_offset.additional_properties = d
        return get_docking_offset

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
