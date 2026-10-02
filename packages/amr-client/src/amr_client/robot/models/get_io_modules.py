from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetIoModules")


@_attrs_define
class GetIoModules:
    """
    Attributes:
        guid (str | Unset): The global unique id across robots that identifies this io module
        name (str | Unset): The name of the io module
        type_ (str | Unset): The type of the io module. currently supported devices [wise].
        url (str | Unset): The URL of the resource
    """

    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    type_: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        name = self.name

        type_ = self.type_

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        get_io_modules = cls(
            guid=guid,
            name=name,
            type_=type_,
            url=url,
        )

        get_io_modules.additional_properties = d
        return get_io_modules

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
