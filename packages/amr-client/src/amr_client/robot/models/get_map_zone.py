from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMapZone")


@_attrs_define
class GetMapZone:
    """
    Attributes:
        guid (str | Unset): The global id unique across robots that identifies this area
        map_ (str | Unset): The url to the map this area belongs to
        name (str | Unset): A name associated with this area
        type_id (int | Unset): The type of area
        url (str | Unset): The URL of the resource
    """

    guid: str | Unset = UNSET
    map_: str | Unset = UNSET
    name: str | Unset = UNSET
    type_id: int | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        map_ = self.map_

        name = self.name

        type_id = self.type_id

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if map_ is not UNSET:
            field_dict["map"] = map_
        if name is not UNSET:
            field_dict["name"] = name
        if type_id is not UNSET:
            field_dict["type_id"] = type_id
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        map_ = d.pop("map", UNSET)

        name = d.pop("name", UNSET)

        type_id = d.pop("type_id", UNSET)

        url = d.pop("url", UNSET)

        get_map_zone = cls(
            guid=guid,
            map_=map_,
            name=name,
            type_id=type_id,
            url=url,
        )

        get_map_zone.additional_properties = d
        return get_map_zone

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
