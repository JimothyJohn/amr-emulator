from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SoundAndLightZone")


@_attrs_define
class SoundAndLightZone:
    """
    Attributes:
        sound_id (None | str | Unset):
        volume (int | Unset):
        light (bool | Unset):
    """

    sound_id: None | str | Unset = UNSET
    volume: int | Unset = UNSET
    light: bool | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        sound_id: None | str | Unset
        if isinstance(self.sound_id, Unset):
            sound_id = UNSET
        else:
            sound_id = self.sound_id

        volume = self.volume

        light = self.light

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if sound_id is not UNSET:
            field_dict["sound-id"] = sound_id
        if volume is not UNSET:
            field_dict["volume"] = volume
        if light is not UNSET:
            field_dict["light"] = light

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_sound_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sound_id = _parse_sound_id(d.pop("sound-id", UNSET))

        volume = d.pop("volume", UNSET)

        light = d.pop("light", UNSET)

        sound_and_light_zone = cls(
            sound_id=sound_id,
            volume=volume,
            light=light,
        )

        return sound_and_light_zone
