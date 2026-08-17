from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="MapsResponse")


@_attrs_define
class MapsResponse:
    """
    Attributes:
        maps (list[GuidAndName]):
    """

    maps: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        maps = []
        for maps_item_data in self.maps:
            maps_item = maps_item_data.to_dict()
            maps.append(maps_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "maps": maps,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        maps = []
        _maps = d.pop("maps")
        for maps_item_data in _maps:
            maps_item = GuidAndName.from_dict(maps_item_data)

            maps.append(maps_item)

        maps_response = cls(
            maps=maps,
        )

        return maps_response
