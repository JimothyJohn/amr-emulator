from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="PositionsResponse")


@_attrs_define
class PositionsResponse:
    """
    Attributes:
        positions (list[GuidAndName]):
    """

    positions: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        positions = []
        for positions_item_data in self.positions:
            positions_item = positions_item_data.to_dict()
            positions.append(positions_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "positions": positions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        positions = []
        _positions = d.pop("positions")
        for positions_item_data in _positions:
            positions_item = GuidAndName.from_dict(positions_item_data)

            positions.append(positions_item)

        positions_response = cls(
            positions=positions,
        )

        return positions_response
