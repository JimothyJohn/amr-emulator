from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostIoModules")


@_attrs_define
class PostIoModules:
    """
    Attributes:
        address (str):
        name (str): Min length: 1, Max length: 255
        created_by_id (str | Unset):
        guid (str | Unset):
        num_inputs (int | Unset):
        num_outputs (int | Unset):
        type_ (str | Unset):
    """

    address: str
    name: str
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    num_inputs: int | Unset = UNSET
    num_outputs: int | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        address = self.address

        name = self.name

        created_by_id = self.created_by_id

        guid = self.guid

        num_inputs = self.num_inputs

        num_outputs = self.num_outputs

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "address": address,
                "name": name,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
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
        address = d.pop("address")

        name = d.pop("name")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        num_inputs = d.pop("num_inputs", UNSET)

        num_outputs = d.pop("num_outputs", UNSET)

        type_ = d.pop("type", UNSET)

        post_io_modules = cls(
            address=address,
            name=name,
            created_by_id=created_by_id,
            guid=guid,
            num_inputs=num_inputs,
            num_outputs=num_outputs,
            type_=type_,
        )

        post_io_modules.additional_properties = d
        return post_io_modules

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
