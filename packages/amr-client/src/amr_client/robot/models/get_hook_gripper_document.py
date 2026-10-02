from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetHookGripperDocument")


@_attrs_define
class GetHookGripperDocument:
    """
    Attributes:
        closed (bool | Unset): Whether the gripper of the hook is closed or not
        state (int | Unset): The sate of the hook gripper in machine format
        state_string (str | Unset): The state of the hook gripper in human format
    """

    closed: bool | Unset = UNSET
    state: int | Unset = UNSET
    state_string: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        closed = self.closed

        state = self.state

        state_string = self.state_string

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if closed is not UNSET:
            field_dict["closed"] = closed
        if state is not UNSET:
            field_dict["state"] = state
        if state_string is not UNSET:
            field_dict["state_string"] = state_string

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        closed = d.pop("closed", UNSET)

        state = d.pop("state", UNSET)

        state_string = d.pop("state_string", UNSET)

        get_hook_gripper_document = cls(
            closed=closed,
            state=state,
            state_string=state_string,
        )

        get_hook_gripper_document.additional_properties = d
        return get_hook_gripper_document

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
