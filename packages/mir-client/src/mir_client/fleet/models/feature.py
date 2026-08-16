from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.feature_properties import FeatureProperties
    from ..models.geometry_double import GeometryDouble
    from ..models.geometry_multi import GeometryMulti
    from ..models.geometry_single import GeometrySingle
    from ..models.geometry_triple import GeometryTriple


T = TypeVar("T", bound="Feature")


@_attrs_define
class Feature:
    """
    Attributes:
        type_ (str):
        properties (FeatureProperties):
        geometry (GeometryDouble | GeometryMulti | GeometrySingle | GeometryTriple):
    """

    type_: str
    properties: FeatureProperties
    geometry: GeometryDouble | GeometryMulti | GeometrySingle | GeometryTriple

    def to_dict(self) -> dict[str, Any]:
        from ..models.geometry_double import GeometryDouble
        from ..models.geometry_multi import GeometryMulti
        from ..models.geometry_single import GeometrySingle

        type_ = self.type_

        properties = self.properties.to_dict()

        geometry: dict[str, Any]
        if isinstance(self.geometry, GeometryDouble):
            geometry = self.geometry.to_dict()
        elif isinstance(self.geometry, GeometryMulti):
            geometry = self.geometry.to_dict()
        elif isinstance(self.geometry, GeometrySingle):
            geometry = self.geometry.to_dict()
        else:
            geometry = self.geometry.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "properties": properties,
                "geometry": geometry,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.feature_properties import FeatureProperties
        from ..models.geometry_double import GeometryDouble
        from ..models.geometry_multi import GeometryMulti
        from ..models.geometry_single import GeometrySingle
        from ..models.geometry_triple import GeometryTriple

        d = dict(src_dict)
        type_ = d.pop("type")

        properties = FeatureProperties.from_dict(d.pop("properties"))

        def _parse_geometry(
            data: object,
        ) -> GeometryDouble | GeometryMulti | GeometrySingle | GeometryTriple:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                geometry_type_0 = GeometryDouble.from_dict(data)

                return geometry_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                geometry_type_1 = GeometryMulti.from_dict(data)

                return geometry_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                geometry_type_2 = GeometrySingle.from_dict(data)

                return geometry_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            geometry_type_3 = GeometryTriple.from_dict(data)

            return geometry_type_3

        geometry = _parse_geometry(d.pop("geometry"))

        feature = cls(
            type_=type_,
            properties=properties,
            geometry=geometry,
        )

        return feature
