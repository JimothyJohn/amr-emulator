from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.module_type import ModuleType

T = TypeVar("T", bound="IoModule")


@_attrs_define
class IoModule:
    """
    Attributes:
        name (str):
        type_ (ModuleType):
        address (str):
        num_inputs (int):
        num_outputs (int):
    """

    name: str
    type_: ModuleType
    address: str
    num_inputs: int
    num_outputs: int

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_.value

        address = self.address

        num_inputs = self.num_inputs

        num_outputs = self.num_outputs

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "type": type_,
                "address": address,
                "num-inputs": num_inputs,
                "num-outputs": num_outputs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_ = ModuleType(d.pop("type"))

        address = d.pop("address")

        num_inputs = d.pop("num-inputs")

        num_outputs = d.pop("num-outputs")

        io_module = cls(
            name=name,
            type_=type_,
            address=address,
            num_inputs=num_inputs,
            num_outputs=num_outputs,
        )

        return io_module
