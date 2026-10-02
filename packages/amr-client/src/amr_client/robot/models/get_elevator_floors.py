from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetElevatorFloors")


@_attrs_define
class GetElevatorFloors:
    """
    Attributes:
        guid (str | Unset): The global id unique across robots that identifies this elevator floor
        map_ (str | Unset):
        map_guid (str | Unset): The map id associated with the floor
        url (str | Unset): The URL of the resource
    """

    guid: str | Unset = UNSET
    map_: str | Unset = UNSET
    map_guid: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        map_ = self.map_

        map_guid = self.map_guid

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if map_ is not UNSET:
            field_dict["map"] = map_
        if map_guid is not UNSET:
            field_dict["map_guid"] = map_guid
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        map_ = d.pop("map", UNSET)

        map_guid = d.pop("map_guid", UNSET)

        url = d.pop("url", UNSET)

        get_elevator_floors = cls(
            guid=guid,
            map_=map_,
            map_guid=map_guid,
            url=url,
        )

        get_elevator_floors.additional_properties = d
        return get_elevator_floors

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
