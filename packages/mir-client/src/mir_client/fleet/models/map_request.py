from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.map_ import Map


T = TypeVar("T", bound="MapRequest")


@_attrs_define
class MapRequest:
    """
    Attributes:
        map_ (Map):
    """

    map_: Map

    def to_dict(self) -> dict[str, Any]:
        map_ = self.map_.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "map": map_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.map_ import Map

        d = dict(src_dict)
        map_ = Map.from_dict(d.pop("map"))

        map_request = cls(
            map_=map_,
        )

        return map_request
