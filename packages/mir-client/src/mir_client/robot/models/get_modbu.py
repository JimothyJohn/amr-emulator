from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_modbu_registers_item import GetModbuRegistersItem


T = TypeVar("T", bound="GetModbu")


@_attrs_define
class GetModbu:
    """
    Attributes:
        data_type (str | Unset): The data type needed
        description (str | Unset): A more detailed explanation of the attribute
        id (int | Unset): The id of the modbus entry
        permissions (str | Unset): If it is allowed to read or write this element
        registers (list[GetModbuRegistersItem] | Unset): The registers on the plc where the data will be stored
        title (str | Unset): A textual description of the desired element
        type_ (str | Unset): The endpoint to which the element refers
    """

    data_type: str | Unset = UNSET
    description: str | Unset = UNSET
    id: int | Unset = UNSET
    permissions: str | Unset = UNSET
    registers: list[GetModbuRegistersItem] | Unset = UNSET
    title: str | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_type = self.data_type

        description = self.description

        id = self.id

        permissions = self.permissions

        registers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.registers, Unset):
            registers = []
            for registers_item_data in self.registers:
                registers_item = registers_item_data.to_dict()
                registers.append(registers_item)

        title = self.title

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data_type is not UNSET:
            field_dict["data_type"] = data_type
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if registers is not UNSET:
            field_dict["registers"] = registers
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_modbu_registers_item import GetModbuRegistersItem

        d = dict(src_dict)
        data_type = d.pop("data_type", UNSET)

        description = d.pop("description", UNSET)

        id = d.pop("id", UNSET)

        permissions = d.pop("permissions", UNSET)

        _registers = d.pop("registers", UNSET)
        registers: list[GetModbuRegistersItem] | Unset = UNSET
        if _registers is not UNSET:
            registers = []
            for registers_item_data in _registers:
                registers_item = GetModbuRegistersItem.from_dict(registers_item_data)

                registers.append(registers_item)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        get_modbu = cls(
            data_type=data_type,
            description=description,
            id=id,
            permissions=permissions,
            registers=registers,
            title=title,
            type_=type_,
        )

        get_modbu.additional_properties = d
        return get_modbu

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
