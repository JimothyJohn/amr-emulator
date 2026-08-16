from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="CartsResponse")


@_attrs_define
class CartsResponse:
    """
    Attributes:
        carts (list[GuidAndName]):
    """

    carts: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        carts = []
        for carts_item_data in self.carts:
            carts_item = carts_item_data.to_dict()
            carts.append(carts_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "carts": carts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        carts = []
        _carts = d.pop("carts")
        for carts_item_data in _carts:
            carts_item = GuidAndName.from_dict(carts_item_data)

            carts.append(carts_item)

        carts_response = cls(
            carts=carts,
        )

        return carts_response
