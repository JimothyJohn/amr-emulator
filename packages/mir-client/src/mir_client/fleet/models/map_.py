from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geo_json import GeoJson


T = TypeVar("T", bound="Map")


@_attrs_define
class Map:
    """
    Attributes:
        name (str):
        geo_json (GeoJson):
        id (None | Unset | UUID):
    """

    name: str
    geo_json: GeoJson
    id: None | Unset | UUID = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        geo_json = self.geo_json.to_dict()

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        elif isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "geo-json": geo_json,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geo_json import GeoJson

        d = dict(src_dict)
        name = d.pop("name")

        geo_json = GeoJson.from_dict(d.pop("geo-json"))

        def _parse_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                id_type_0 = UUID(data)

                return id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        id = _parse_id(d.pop("id", UNSET))

        map_ = cls(
            name=name,
            geo_json=geo_json,
            id=id,
        )

        return map_
