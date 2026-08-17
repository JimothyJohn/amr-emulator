from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetHookHeightDocument")


@_attrs_define
class GetHookHeightDocument:
    """
    Attributes:
        height (int | Unset): The height of the hook in mm
        state (int | Unset): The state of the hook actuator in machine format
        state_string (str | Unset): The state of the hook actuator in human format
    """

    height: int | Unset = UNSET
    state: int | Unset = UNSET
    state_string: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        height = self.height

        state = self.state

        state_string = self.state_string

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if height is not UNSET:
            field_dict["height"] = height
        if state is not UNSET:
            field_dict["state"] = state
        if state_string is not UNSET:
            field_dict["state_string"] = state_string

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        height = d.pop("height", UNSET)

        state = d.pop("state", UNSET)

        state_string = d.pop("state_string", UNSET)

        get_hook_height_document = cls(
            height=height,
            state=state,
            state_string=state_string,
        )

        get_hook_height_document.additional_properties = d
        return get_hook_height_document

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
