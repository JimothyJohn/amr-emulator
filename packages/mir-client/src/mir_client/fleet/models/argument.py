from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.parameter_type import ParameterType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Argument")


@_attrs_define
class Argument:
    """
    Attributes:
        type_ (ParameterType):
        name (str | Unset):
        default_value (str | Unset):
    """

    type_: ParameterType
    name: str | Unset = UNSET
    default_value: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        name = self.name

        default_value = self.default_value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if default_value is not UNSET:
            field_dict["default-value"] = default_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = ParameterType(d.pop("type"))

        name = d.pop("name", UNSET)

        default_value = d.pop("default-value", UNSET)

        argument = cls(
            type_=type_,
            name=name,
            default_value=default_value,
        )

        return argument
