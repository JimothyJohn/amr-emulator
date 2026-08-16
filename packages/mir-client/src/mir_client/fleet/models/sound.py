from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Sound")


@_attrs_define
class Sound:
    """
    Attributes:
        name (str):
        volume (int):
        note (str):
        duration (str):
    """

    name: str
    volume: int
    note: str
    duration: str

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        volume = self.volume

        note = self.note

        duration = self.duration

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "volume": volume,
                "note": note,
                "duration": duration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        volume = d.pop("volume")

        note = d.pop("note")

        duration = d.pop("duration")

        sound = cls(
            name=name,
            volume=volume,
            note=note,
            duration=duration,
        )

        return sound
