from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.feature import Feature


T = TypeVar("T", bound="GeoJson")


@_attrs_define
class GeoJson:
    """
    Attributes:
        type_ (str):
        features (list[Feature]):
    """

    type_: str
    features: list[Feature]

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        features = []
        for features_item_data in self.features:
            features_item = features_item_data.to_dict()
            features.append(features_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "features": features,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.feature import Feature

        d = dict(src_dict)
        type_ = d.pop("type")

        features = []
        _features = d.pop("features")
        for features_item_data in _features:
            features_item = Feature.from_dict(features_item_data)

            features.append(features_item)

        geo_json = cls(
            type_=type_,
            features=features,
        )

        return geo_json
