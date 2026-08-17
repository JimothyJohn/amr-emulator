from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetStatusErrorsItem")


@_attrs_define
class GetStatusErrorsItem:
    """
    Attributes:
        code (int | Unset): The error code
        description (str | Unset): Description of the error
        module (str | Unset): The module reporting the error
        non_resettable (bool | Unset): The error cannot be reset from ui
    """

    code: int | Unset = UNSET
    description: str | Unset = UNSET
    module: str | Unset = UNSET
    non_resettable: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        description = self.description

        module = self.module

        non_resettable = self.non_resettable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if description is not UNSET:
            field_dict["description"] = description
        if module is not UNSET:
            field_dict["module"] = module
        if non_resettable is not UNSET:
            field_dict["non_resettable"] = non_resettable

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code", UNSET)

        description = d.pop("description", UNSET)

        module = d.pop("module", UNSET)

        non_resettable = d.pop("non_resettable", UNSET)

        get_status_errors_item = cls(
            code=code,
            description=description,
            module=module,
            non_resettable=non_resettable,
        )

        get_status_errors_item.additional_properties = d
        return get_status_errors_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
