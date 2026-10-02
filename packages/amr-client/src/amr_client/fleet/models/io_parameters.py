from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="IoParameters")


@_attrs_define
class IoParameters:
    """
    Attributes:
        io_module_id (str):
        io_module_pin_port (int | None | Unset):
    """

    io_module_id: str
    io_module_pin_port: int | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        io_module_id = self.io_module_id

        io_module_pin_port: int | None | Unset
        if isinstance(self.io_module_pin_port, Unset):
            io_module_pin_port = UNSET
        else:
            io_module_pin_port = self.io_module_pin_port

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "io-module-id": io_module_id,
            }
        )
        if io_module_pin_port is not UNSET:
            field_dict["io-module-pin-port"] = io_module_pin_port

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        io_module_id = d.pop("io-module-id")

        def _parse_io_module_pin_port(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        io_module_pin_port = _parse_io_module_pin_port(d.pop("io-module-pin-port", UNSET))

        io_parameters = cls(
            io_module_id=io_module_id,
            io_module_pin_port=io_module_pin_port,
        )

        return io_parameters
