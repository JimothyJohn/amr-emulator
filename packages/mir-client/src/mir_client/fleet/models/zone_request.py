from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.zone_1 import Zone1


T = TypeVar("T", bound="ZoneRequest")


@_attrs_define
class ZoneRequest:
    """
    Attributes:
        zone (Zone1):
    """

    zone: Zone1

    def to_dict(self) -> dict[str, Any]:
        zone = self.zone.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "zone": zone,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.zone_1 import Zone1

        d = dict(src_dict)
        zone = Zone1.from_dict(d.pop("zone"))

        zone_request = cls(
            zone=zone,
        )

        return zone_request
