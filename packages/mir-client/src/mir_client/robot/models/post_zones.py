from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_zones_actions_item import PostZonesActionsItem
    from ..models.post_zones_polygon_item import PostZonesPolygonItem


T = TypeVar("T", bound="PostZones")


@_attrs_define
class PostZones:
    """
    Attributes:
        map_id (str):
        polygon (list[PostZonesPolygonItem]):
        type_id (int):
        actions (list[PostZonesActionsItem] | Unset):
        created_by_id (str | Unset):
        direction (float | Unset):
        guid (str | Unset):
        name (str | Unset): Max length: 255
        shape_type (str | Unset):
        stroke_width (float | Unset):
    """

    map_id: str
    polygon: list[PostZonesPolygonItem]
    type_id: int
    actions: list[PostZonesActionsItem] | Unset = UNSET
    created_by_id: str | Unset = UNSET
    direction: float | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    shape_type: str | Unset = UNSET
    stroke_width: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        map_id = self.map_id

        polygon = []
        for polygon_item_data in self.polygon:
            polygon_item = polygon_item_data.to_dict()
            polygon.append(polygon_item)

        type_id = self.type_id

        actions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for actions_item_data in self.actions:
                actions_item = actions_item_data.to_dict()
                actions.append(actions_item)

        created_by_id = self.created_by_id

        direction = self.direction

        guid = self.guid

        name = self.name

        shape_type = self.shape_type

        stroke_width = self.stroke_width

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "map_id": map_id,
                "polygon": polygon,
                "type_id": type_id,
            }
        )
        if actions is not UNSET:
            field_dict["actions"] = actions
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if direction is not UNSET:
            field_dict["direction"] = direction
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if shape_type is not UNSET:
            field_dict["shape_type"] = shape_type
        if stroke_width is not UNSET:
            field_dict["stroke_width"] = stroke_width

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_zones_actions_item import PostZonesActionsItem
        from ..models.post_zones_polygon_item import PostZonesPolygonItem

        d = dict(src_dict)
        map_id = d.pop("map_id")

        polygon = []
        _polygon = d.pop("polygon")
        for polygon_item_data in _polygon:
            polygon_item = PostZonesPolygonItem.from_dict(polygon_item_data)

            polygon.append(polygon_item)

        type_id = d.pop("type_id")

        _actions = d.pop("actions", UNSET)
        actions: list[PostZonesActionsItem] | Unset = UNSET
        if _actions is not UNSET:
            actions = []
            for actions_item_data in _actions:
                actions_item = PostZonesActionsItem.from_dict(actions_item_data)

                actions.append(actions_item)

        created_by_id = d.pop("created_by_id", UNSET)

        direction = d.pop("direction", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        shape_type = d.pop("shape_type", UNSET)

        stroke_width = d.pop("stroke_width", UNSET)

        post_zones = cls(
            map_id=map_id,
            polygon=polygon,
            type_id=type_id,
            actions=actions,
            created_by_id=created_by_id,
            direction=direction,
            guid=guid,
            name=name,
            shape_type=shape_type,
            stroke_width=stroke_width,
        )

        post_zones.additional_properties = d
        return post_zones

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
