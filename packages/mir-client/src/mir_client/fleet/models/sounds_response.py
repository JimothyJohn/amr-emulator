from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="SoundsResponse")


@_attrs_define
class SoundsResponse:
    """
    Attributes:
        sounds (list[GuidAndName]):
    """

    sounds: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        sounds = []
        for sounds_item_data in self.sounds:
            sounds_item = sounds_item_data.to_dict()
            sounds.append(sounds_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sounds": sounds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        sounds = []
        _sounds = d.pop("sounds")
        for sounds_item_data in _sounds:
            sounds_item = GuidAndName.from_dict(sounds_item_data)

            sounds.append(sounds_item)

        sounds_response = cls(
            sounds=sounds,
        )

        return sounds_response
