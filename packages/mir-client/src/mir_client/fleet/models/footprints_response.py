from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="FootprintsResponse")


@_attrs_define
class FootprintsResponse:
    """
    Attributes:
        footprints (list[GuidAndName]):
    """

    footprints: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        footprints = []
        for footprints_item_data in self.footprints:
            footprints_item = footprints_item_data.to_dict()
            footprints.append(footprints_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "footprints": footprints,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        footprints = []
        _footprints = d.pop("footprints")
        for footprints_item_data in _footprints:
            footprints_item = GuidAndName.from_dict(footprints_item_data)

            footprints.append(footprints_item)

        footprints_response = cls(
            footprints=footprints,
        )

        return footprints_response
