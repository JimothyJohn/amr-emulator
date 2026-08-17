from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetIoModule")


@_attrs_define
class GetIoModule:
    """
    Attributes:
        address (str | Unset): The address for connecting to the device. it can be a mac address or an ip depending on
            the type of io module
        created_by (str | Unset): The url to the description of the type of this io module
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global unique id across robots that identifies this io module
        name (str | Unset): The name of the io module
        num_inputs (int | Unset): The number of inputs that the io module has
        num_outputs (int | Unset): The number or outputs that the io module has
        type_ (str | Unset): The type of the io module. currently supported devices [wise].
    """

    address: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    num_inputs: int | Unset = UNSET
    num_outputs: int | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        address = self.address

        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        name = self.name

        num_inputs = self.num_inputs

        num_outputs = self.num_outputs

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if address is not UNSET:
            field_dict["address"] = address
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
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

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        num_inputs = d.pop("num_inputs", UNSET)

        num_outputs = d.pop("num_outputs", UNSET)

        type_ = d.pop("type", UNSET)

        get_io_module = cls(
            address=address,
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            name=name,
            num_inputs=num_inputs,
            num_outputs=num_outputs,
            type_=type_,
        )

        get_io_module.additional_properties = d
        return get_io_module

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
