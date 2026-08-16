from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetRegisters")


@_attrs_define
class GetRegisters:
    """
    Attributes:
        id (int | Unset): The index of the register
        label (str | Unset): A label for the register
        url (str | Unset): The URL of the resource
        value (float | Unset): The value of the register
    """

    id: int | Unset = UNSET
    label: str | Unset = UNSET
    url: str | Unset = UNSET
    value: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        label = self.label

        url = self.url

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if label is not UNSET:
            field_dict["label"] = label
        if url is not UNSET:
            field_dict["url"] = url
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        label = d.pop("label", UNSET)

        url = d.pop("url", UNSET)

        value = d.pop("value", UNSET)

        get_registers = cls(
            id=id,
            label=label,
            url=url,
            value=value,
        )

        get_registers.additional_properties = d
        return get_registers

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
