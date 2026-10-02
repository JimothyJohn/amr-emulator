from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDockingOffsets")


@_attrs_define
class GetDockingOffsets:
    """
    Attributes:
        guid (str | Unset): The global id unique across robots that identifies this docking offset
        name (str | Unset): The name of the docking offset. used for docking offset independent from positions.
        position (str | Unset): The url to the position
        url (str | Unset): The URL of the resource
    """

    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    position: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        name = self.name

        position = self.position

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if position is not UNSET:
            field_dict["position"] = position
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        position = d.pop("position", UNSET)

        url = d.pop("url", UNSET)

        get_docking_offsets = cls(
            guid=guid,
            name=name,
            position=position,
            url=url,
        )

        get_docking_offsets.additional_properties = d
        return get_docking_offsets

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
