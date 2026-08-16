from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.serial_order import SerialOrder


T = TypeVar("T", bound="SerialOrderRequest")


@_attrs_define
class SerialOrderRequest:
    """
    Attributes:
        serial_order (SerialOrder):
    """

    serial_order: SerialOrder

    def to_dict(self) -> dict[str, Any]:
        serial_order = self.serial_order.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "serial-order": serial_order,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.serial_order import SerialOrder

        d = dict(src_dict)
        serial_order = SerialOrder.from_dict(d.pop("serial-order"))

        serial_order_request = cls(
            serial_order=serial_order,
        )

        return serial_order_request
