from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.plc_action import PlcAction
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlcParameters")


@_attrs_define
class PlcParameters:
    """
    Attributes:
        register (int | Unset):
        action (PlcAction | Unset):
        value (int | Unset):
    """

    register: int | Unset = UNSET
    action: PlcAction | Unset = UNSET
    value: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        register = self.register

        action: str | Unset = UNSET
        if not isinstance(self.action, Unset):
            action = self.action.value

        value = self.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if register is not UNSET:
            field_dict["register"] = register
        if action is not UNSET:
            field_dict["action"] = action
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        register = d.pop("register", UNSET)

        _action = d.pop("action", UNSET)
        action: PlcAction | Unset
        if isinstance(_action, Unset):
            action = UNSET
        else:
            action = PlcAction(_action)

        value = d.pop("value", UNSET)

        plc_parameters = cls(
            register=register,
            action=action,
            value=value,
        )

        return plc_parameters
