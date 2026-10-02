from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSounds")


@_attrs_define
class GetSounds:
    """
    Attributes:
        guid (str | Unset): The global id unique across robots that identifies this sound
        length (str | Unset): The length of the sound in the format hh:mm:ss
        name (str | Unset): The name of the sound
        url (str | Unset): The URL of the resource
        volume (int | Unset): The volumne of the sound when played
    """

    guid: str | Unset = UNSET
    length: str | Unset = UNSET
    name: str | Unset = UNSET
    url: str | Unset = UNSET
    volume: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        length = self.length

        name = self.name

        url = self.url

        volume = self.volume

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if length is not UNSET:
            field_dict["length"] = length
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url
        if volume is not UNSET:
            field_dict["volume"] = volume

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        length = d.pop("length", UNSET)

        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        volume = d.pop("volume", UNSET)

        get_sounds = cls(
            guid=guid,
            length=length,
            name=name,
            url=url,
            volume=volume,
        )

        get_sounds.additional_properties = d
        return get_sounds

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
