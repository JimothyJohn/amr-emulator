from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetModbusMissions")


@_attrs_define
class GetModbusMissions:
    """
    Attributes:
        coil_id (int | Unset): The id of the coil to trigger the mission
        guid (str | Unset): The global id unique across robots that identifies this modbus mission
        url (str | Unset): The URL of the resource
    """

    coil_id: int | Unset = UNSET
    guid: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        coil_id = self.coil_id

        guid = self.guid

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if coil_id is not UNSET:
            field_dict["coil_id"] = coil_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        coil_id = d.pop("coil_id", UNSET)

        guid = d.pop("guid", UNSET)

        url = d.pop("url", UNSET)

        get_modbus_missions = cls(
            coil_id=coil_id,
            guid=guid,
            url=url,
        )

        get_modbus_missions.additional_properties = d
        return get_modbus_missions

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
