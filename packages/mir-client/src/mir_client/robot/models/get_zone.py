from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_zone_actions import GetZoneActions
    from ..models.get_zone_polygon_item import GetZonePolygonItem


T = TypeVar("T", bound="GetZone")


@_attrs_define
class GetZone:
    """
    Attributes:
        actions (GetZoneActions | Unset):
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        direction (float | Unset): Direction of one way area
        guid (str | Unset): The global id unique across robots that identifies this area
        map_ (str | Unset): The url to the map this area belongs to
        map_id (str | Unset): The id of the map this area belongs to
        name (str | Unset): A name associated with this area
        polygon (list[GetZonePolygonItem] | Unset): The list of coordinates in the area polygon
        shape_type (str | Unset): The type of the area shape
        stroke_width (float | Unset): Width of stroke if shape type is stroke
        type_id (int | Unset): The type of area
    """

    actions: GetZoneActions | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    direction: float | Unset = UNSET
    guid: str | Unset = UNSET
    map_: str | Unset = UNSET
    map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    polygon: list[GetZonePolygonItem] | Unset = UNSET
    shape_type: str | Unset = UNSET
    stroke_width: float | Unset = UNSET
    type_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        created_by = self.created_by

        created_by_id = self.created_by_id

        direction = self.direction

        guid = self.guid

        map_ = self.map_

        map_id = self.map_id

        name = self.name

        polygon: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.polygon, Unset):
            polygon = []
            for polygon_item_data in self.polygon:
                polygon_item = polygon_item_data.to_dict()
                polygon.append(polygon_item)

        shape_type = self.shape_type

        stroke_width = self.stroke_width

        type_id = self.type_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if direction is not UNSET:
            field_dict["direction"] = direction
        if guid is not UNSET:
            field_dict["guid"] = guid
        if map_ is not UNSET:
            field_dict["map"] = map_
        if map_id is not UNSET:
            field_dict["map_id"] = map_id
        if name is not UNSET:
            field_dict["name"] = name
        if polygon is not UNSET:
            field_dict["polygon"] = polygon
        if shape_type is not UNSET:
            field_dict["shape_type"] = shape_type
        if stroke_width is not UNSET:
            field_dict["stroke_width"] = stroke_width
        if type_id is not UNSET:
            field_dict["type_id"] = type_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_zone_actions import GetZoneActions
        from ..models.get_zone_polygon_item import GetZonePolygonItem

        d = dict(src_dict)
        _actions = d.pop("actions", UNSET)
        actions: GetZoneActions | Unset
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = GetZoneActions.from_dict(_actions)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        direction = d.pop("direction", UNSET)

        guid = d.pop("guid", UNSET)

        map_ = d.pop("map", UNSET)

        map_id = d.pop("map_id", UNSET)

        name = d.pop("name", UNSET)

        _polygon = d.pop("polygon", UNSET)
        polygon: list[GetZonePolygonItem] | Unset = UNSET
        if _polygon is not UNSET:
            polygon = []
            for polygon_item_data in _polygon:
                polygon_item = GetZonePolygonItem.from_dict(polygon_item_data)

                polygon.append(polygon_item)

        shape_type = d.pop("shape_type", UNSET)

        stroke_width = d.pop("stroke_width", UNSET)

        type_id = d.pop("type_id", UNSET)

        get_zone = cls(
            actions=actions,
            created_by=created_by,
            created_by_id=created_by_id,
            direction=direction,
            guid=guid,
            map_=map_,
            map_id=map_id,
            name=name,
            polygon=polygon,
            shape_type=shape_type,
            stroke_width=stroke_width,
            type_id=type_id,
        )

        get_zone.additional_properties = d
        return get_zone

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
