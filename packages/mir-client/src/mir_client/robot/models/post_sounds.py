from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, Unset

T = TypeVar("T", bound="PostSounds")


@_attrs_define
class PostSounds:
    """
    Attributes:
        name (str): Min length: 1, Max length: 40
        sound (File):
        created_by_id (str | Unset):
        guid (str | Unset):
        note (str | Unset): Max length: 255
        volume (int | Unset):
    """

    name: str
    sound: File
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    note: str | Unset = UNSET
    volume: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        sound = self.sound.to_tuple()

        created_by_id = self.created_by_id

        guid = self.guid

        note = self.note

        volume = self.volume

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "sound": sound,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if note is not UNSET:
            field_dict["note"] = note
        if volume is not UNSET:
            field_dict["volume"] = volume

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        sound = File(payload=BytesIO(d.pop("sound")))

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        note = d.pop("note", UNSET)

        volume = d.pop("volume", UNSET)

        post_sounds = cls(
            name=name,
            sound=sound,
            created_by_id=created_by_id,
            guid=guid,
            note=note,
            volume=volume,
        )

        post_sounds.additional_properties = d
        return post_sounds

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
