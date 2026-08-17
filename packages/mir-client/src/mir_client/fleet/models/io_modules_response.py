from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="IoModulesResponse")


@_attrs_define
class IoModulesResponse:
    """
    Attributes:
        io_modules (list[GuidAndName]):
    """

    io_modules: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        io_modules = []
        for io_modules_item_data in self.io_modules:
            io_modules_item = io_modules_item_data.to_dict()
            io_modules.append(io_modules_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "io-modules": io_modules,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        io_modules = []
        _io_modules = d.pop("io-modules")
        for io_modules_item_data in _io_modules:
            io_modules_item = GuidAndName.from_dict(io_modules_item_data)

            io_modules.append(io_modules_item)

        io_modules_response = cls(
            io_modules=io_modules,
        )

        return io_modules_response
