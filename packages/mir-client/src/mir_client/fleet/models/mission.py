from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.argument import Argument


T = TypeVar("T", bound="Mission")


@_attrs_define
class Mission:
    """
    Attributes:
        name (str | Unset):
        arguments (list[Argument] | Unset):
    """

    name: str | Unset = UNSET
    arguments: list[Argument] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        arguments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.arguments, Unset):
            arguments = []
            for arguments_item_data in self.arguments:
                arguments_item = arguments_item_data.to_dict()
                arguments.append(arguments_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if arguments is not UNSET:
            field_dict["arguments"] = arguments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.argument import Argument

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _arguments = d.pop("arguments", UNSET)
        arguments: list[Argument] | Unset = UNSET
        if _arguments is not UNSET:
            arguments = []
            for arguments_item_data in _arguments:
                arguments_item = Argument.from_dict(arguments_item_data)

                arguments.append(arguments_item)

        mission = cls(
            name=name,
            arguments=arguments,
        )

        return mission
