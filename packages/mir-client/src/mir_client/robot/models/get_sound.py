from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSound")


@_attrs_define
class GetSound:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global id unique across robots that identifies this sound
        length (str | Unset): The length of the sound in the format hh:mm:ss
        name (str | Unset): The name of the sound
        note (str | Unset): A possible description of the sound
        sound (str | Unset): A binary representation of the sound
        stream (str | Unset): The url to stream the raw audio
        volume (int | Unset): The volumne of the sound when played
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    length: str | Unset = UNSET
    name: str | Unset = UNSET
    note: str | Unset = UNSET
    sound: str | Unset = UNSET
    stream: str | Unset = UNSET
    volume: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        length = self.length

        name = self.name

        note = self.note

        sound = self.sound

        stream = self.stream

        volume = self.volume

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if length is not UNSET:
            field_dict["length"] = length
        if name is not UNSET:
            field_dict["name"] = name
        if note is not UNSET:
            field_dict["note"] = note
        if sound is not UNSET:
            field_dict["sound"] = sound
        if stream is not UNSET:
            field_dict["stream"] = stream
        if volume is not UNSET:
            field_dict["volume"] = volume

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        length = d.pop("length", UNSET)

        name = d.pop("name", UNSET)

        note = d.pop("note", UNSET)

        sound = d.pop("sound", UNSET)

        stream = d.pop("stream", UNSET)

        volume = d.pop("volume", UNSET)

        get_sound = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            length=length,
            name=name,
            note=note,
            sound=sound,
            stream=stream,
            volume=volume,
        )

        get_sound.additional_properties = d
        return get_sound

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
