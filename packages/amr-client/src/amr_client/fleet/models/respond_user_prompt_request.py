from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="RespondUserPromptRequest")


@_attrs_define
class RespondUserPromptRequest:
    """
    Attributes:
        id (UUID):
        value (int):
    """

    id: UUID
    value: int

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        value = self.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        value = d.pop("value")

        respond_user_prompt_request = cls(
            id=id,
            value=value,
        )

        return respond_user_prompt_request
