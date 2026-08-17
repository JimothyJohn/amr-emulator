from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.put_zone_actions_item import PutZoneActionsItem
    from ..models.put_zone_polygon_item import PutZonePolygonItem


T = TypeVar("T", bound="PutZone")


@_attrs_define
class PutZone:
    """
    Attributes:
        actions (list[PutZoneActionsItem] | Unset):
        direction (float | Unset):
        name (str | Unset): Max length: 255
        polygon (list[PutZonePolygonItem] | Unset):
        stroke_width (float | Unset):
    """

    actions: list[PutZoneActionsItem] | Unset = UNSET
    direction: float | Unset = UNSET
    name: str | Unset = UNSET
    polygon: list[PutZonePolygonItem] | Unset = UNSET
    stroke_width: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for actions_item_data in self.actions:
                actions_item = actions_item_data.to_dict()
                actions.append(actions_item)

        direction = self.direction

        name = self.name

        polygon: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.polygon, Unset):
            polygon = []
            for polygon_item_data in self.polygon:
                polygon_item = polygon_item_data.to_dict()
                polygon.append(polygon_item)

        stroke_width = self.stroke_width

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if direction is not UNSET:
            field_dict["direction"] = direction
        if name is not UNSET:
            field_dict["name"] = name
        if polygon is not UNSET:
            field_dict["polygon"] = polygon
        if stroke_width is not UNSET:
            field_dict["stroke_width"] = stroke_width

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.put_zone_actions_item import PutZoneActionsItem
        from ..models.put_zone_polygon_item import PutZonePolygonItem

        d = dict(src_dict)
        _actions = d.pop("actions", UNSET)
        actions: list[PutZoneActionsItem] | Unset = UNSET
        if _actions is not UNSET:
            actions = []
            for actions_item_data in _actions:
                actions_item = PutZoneActionsItem.from_dict(actions_item_data)

                actions.append(actions_item)

        direction = d.pop("direction", UNSET)

        name = d.pop("name", UNSET)

        _polygon = d.pop("polygon", UNSET)
        polygon: list[PutZonePolygonItem] | Unset = UNSET
        if _polygon is not UNSET:
            polygon = []
            for polygon_item_data in _polygon:
                polygon_item = PutZonePolygonItem.from_dict(polygon_item_data)

                polygon.append(polygon_item)

        stroke_width = d.pop("stroke_width", UNSET)

        put_zone = cls(
            actions=actions,
            direction=direction,
            name=name,
            polygon=polygon,
            stroke_width=stroke_width,
        )

        put_zone.additional_properties = d
        return put_zone

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
