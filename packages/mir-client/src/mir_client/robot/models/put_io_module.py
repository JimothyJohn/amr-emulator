from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutIoModule")


@_attrs_define
class PutIoModule:
    """
    Attributes:
        address (str | Unset):
        name (str | Unset): Min length: 1, Max length: 255
        num_inputs (int | Unset):
        num_outputs (int | Unset):
        type_ (str | Unset): Choices are: {"wise"}
    """

    address: str | Unset = UNSET
    name: str | Unset = UNSET
    num_inputs: int | Unset = UNSET
    num_outputs: int | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        address = self.address

        name = self.name

        num_inputs = self.num_inputs

        num_outputs = self.num_outputs

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if address is not UNSET:
            field_dict["address"] = address
        if name is not UNSET:
            field_dict["name"] = name
        if num_inputs is not UNSET:
            field_dict["num_inputs"] = num_inputs
        if num_outputs is not UNSET:
            field_dict["num_outputs"] = num_outputs
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        address = d.pop("address", UNSET)

        name = d.pop("name", UNSET)

        num_inputs = d.pop("num_inputs", UNSET)

        num_outputs = d.pop("num_outputs", UNSET)

        type_ = d.pop("type", UNSET)

        put_io_module = cls(
            address=address,
            name=name,
            num_inputs=num_inputs,
            num_outputs=num_outputs,
            type_=type_,
        )

        put_io_module.additional_properties = d
        return put_io_module

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
