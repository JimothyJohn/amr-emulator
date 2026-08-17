from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="UnsubscribeRequest")


@_attrs_define
class UnsubscribeRequest:
    """
    Attributes:
        base_url (str):
    """

    base_url: str

    def to_dict(self) -> dict[str, Any]:
        base_url = self.base_url

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "base-url": base_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        base_url = d.pop("base-url")

        unsubscribe_request = cls(
            base_url=base_url,
        )

        return unsubscribe_request
