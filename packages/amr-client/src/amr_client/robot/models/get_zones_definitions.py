from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetZonesDefinitions")


@_attrs_define
class GetZonesDefinitions:
    """
    Attributes:
        actions (str | Unset):
        color (str | Unset): The color associated with this area
        direction (str | Unset):
        id (int | Unset): The type of area
        image (str | Unset):
        name (str | Unset): A nice name associated with this area action
        shape_types (str | Unset):
        stroke_width (str | Unset):
    """

    actions: str | Unset = UNSET
    color: str | Unset = UNSET
    direction: str | Unset = UNSET
    id: int | Unset = UNSET
    image: str | Unset = UNSET
    name: str | Unset = UNSET
    shape_types: str | Unset = UNSET
    stroke_width: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions = self.actions

        color = self.color

        direction = self.direction

        id = self.id

        image = self.image

        name = self.name

        shape_types = self.shape_types

        stroke_width = self.stroke_width

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if color is not UNSET:
            field_dict["color"] = color
        if direction is not UNSET:
            field_dict["direction"] = direction
        if id is not UNSET:
            field_dict["id"] = id
        if image is not UNSET:
            field_dict["image"] = image
        if name is not UNSET:
            field_dict["name"] = name
        if shape_types is not UNSET:
            field_dict["shape_types"] = shape_types
        if stroke_width is not UNSET:
            field_dict["stroke_width"] = stroke_width

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        actions = d.pop("actions", UNSET)

        color = d.pop("color", UNSET)

        direction = d.pop("direction", UNSET)

        id = d.pop("id", UNSET)

        image = d.pop("image", UNSET)

        name = d.pop("name", UNSET)

        shape_types = d.pop("shape_types", UNSET)

        stroke_width = d.pop("stroke_width", UNSET)

        get_zones_definitions = cls(
            actions=actions,
            color=color,
            direction=direction,
            id=id,
            image=image,
            name=name,
            shape_types=shape_types,
            stroke_width=stroke_width,
        )

        get_zones_definitions.additional_properties = d
        return get_zones_definitions

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
