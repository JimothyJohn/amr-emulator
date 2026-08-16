from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GeometryTriple")


@_attrs_define
class GeometryTriple:
    """
    Attributes:
        type_ (str):
        coordinates (list[list[list[float]]]):
    """

    type_: str
    coordinates: list[list[list[float]]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        coordinates = []
        for coordinates_item_data in self.coordinates:
            coordinates_item = []
            for coordinates_item_item_data in coordinates_item_data:
                coordinates_item_item = coordinates_item_item_data

                coordinates_item.append(coordinates_item_item)

            coordinates.append(coordinates_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "coordinates": coordinates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        coordinates = []
        _coordinates = d.pop("coordinates")
        for coordinates_item_data in _coordinates:
            coordinates_item = []
            _coordinates_item = coordinates_item_data
            for coordinates_item_item_data in _coordinates_item:
                coordinates_item_item = cast(list[float], coordinates_item_item_data)

                coordinates_item.append(coordinates_item_item)

            coordinates.append(coordinates_item)

        geometry_triple = cls(
            type_=type_,
            coordinates=coordinates,
        )

        geometry_triple.additional_properties = d
        return geometry_triple

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
