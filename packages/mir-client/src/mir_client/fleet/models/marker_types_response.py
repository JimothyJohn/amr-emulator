from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="MarkerTypesResponse")


@_attrs_define
class MarkerTypesResponse:
    """
    Attributes:
        marker_types (list[GuidAndName]):
    """

    marker_types: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        marker_types = []
        for marker_types_item_data in self.marker_types:
            marker_types_item = marker_types_item_data.to_dict()
            marker_types.append(marker_types_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "marker-types": marker_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        marker_types = []
        _marker_types = d.pop("marker-types")
        for marker_types_item_data in _marker_types:
            marker_types_item = GuidAndName.from_dict(marker_types_item_data)

            marker_types.append(marker_types_item)

        marker_types_response = cls(
            marker_types=marker_types,
        )

        return marker_types_response
