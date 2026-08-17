from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.key_idle import KeyIdle
    from ..models.key_manual import KeyManual


T = TypeVar("T", bound="Key")


@_attrs_define
class Key:
    """
    Attributes:
        key_manual (KeyManual | Unset):
        key_idle (KeyIdle | Unset):
    """

    key_manual: KeyManual | Unset = UNSET
    key_idle: KeyIdle | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        key_manual: dict[str, Any] | Unset = UNSET
        if not isinstance(self.key_manual, Unset):
            key_manual = self.key_manual.to_dict()

        key_idle: dict[str, Any] | Unset = UNSET
        if not isinstance(self.key_idle, Unset):
            key_idle = self.key_idle.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if key_manual is not UNSET:
            field_dict["key-manual"] = key_manual
        if key_idle is not UNSET:
            field_dict["key-idle"] = key_idle

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.key_idle import KeyIdle
        from ..models.key_manual import KeyManual

        d = dict(src_dict)
        _key_manual = d.pop("key-manual", UNSET)
        key_manual: KeyManual | Unset
        if isinstance(_key_manual, Unset):
            key_manual = UNSET
        else:
            key_manual = KeyManual.from_dict(_key_manual)

        _key_idle = d.pop("key-idle", UNSET)
        key_idle: KeyIdle | Unset
        if isinstance(_key_idle, Unset):
            key_idle = UNSET
        else:
            key_idle = KeyIdle.from_dict(_key_idle)

        key = cls(
            key_manual=key_manual,
            key_idle=key_idle,
        )

        return key
