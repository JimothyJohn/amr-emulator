from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Evacuation")


@_attrs_define
class Evacuation:
    """
    Attributes:
        evacuation_state (str | Unset):
    """

    evacuation_state: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        evacuation_state = self.evacuation_state

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if evacuation_state is not UNSET:
            field_dict["evacuation-state"] = evacuation_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        evacuation_state = d.pop("evacuation-state", UNSET)

        evacuation = cls(
            evacuation_state=evacuation_state,
        )

        return evacuation
