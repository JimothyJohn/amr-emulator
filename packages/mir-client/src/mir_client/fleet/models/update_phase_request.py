from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.phase import Phase


T = TypeVar("T", bound="UpdatePhaseRequest")


@_attrs_define
class UpdatePhaseRequest:
    """
    Attributes:
        serial_order_id (str):
        index (int):
        phase (Phase):
    """

    serial_order_id: str
    index: int
    phase: Phase

    def to_dict(self) -> dict[str, Any]:
        serial_order_id = self.serial_order_id

        index = self.index

        phase = self.phase.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "serial-order-id": serial_order_id,
                "index": index,
                "phase": phase,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.phase import Phase

        d = dict(src_dict)
        serial_order_id = d.pop("serial-order-id")

        index = d.pop("index")

        phase = Phase.from_dict(d.pop("phase"))

        update_phase_request = cls(
            serial_order_id=serial_order_id,
            index=index,
            phase=phase,
        )

        return update_phase_request
