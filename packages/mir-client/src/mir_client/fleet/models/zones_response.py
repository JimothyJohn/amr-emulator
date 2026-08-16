from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="ZonesResponse")


@_attrs_define
class ZonesResponse:
    """
    Attributes:
        zones (list[GuidAndName]):
    """

    zones: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        zones = []
        for zones_item_data in self.zones:
            zones_item = zones_item_data.to_dict()
            zones.append(zones_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "zones": zones,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        zones = []
        _zones = d.pop("zones")
        for zones_item_data in _zones:
            zones_item = GuidAndName.from_dict(zones_item_data)

            zones.append(zones_item)

        zones_response = cls(
            zones=zones,
        )

        return zones_response
