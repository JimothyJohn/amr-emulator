from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetStatusUserPrompt")


@_attrs_define
class GetStatusUserPrompt:
    """
    Attributes:
        guid (str | Unset):
        options (list[str] | Unset):
        question (str | Unset):
        timeout (float | Unset):
        user_group (str | Unset):
    """

    guid: str | Unset = UNSET
    options: list[str] | Unset = UNSET
    question: str | Unset = UNSET
    timeout: float | Unset = UNSET
    user_group: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        options: list[str] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options

        question = self.question

        timeout = self.timeout

        user_group = self.user_group

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if options is not UNSET:
            field_dict["options"] = options
        if question is not UNSET:
            field_dict["question"] = question
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if user_group is not UNSET:
            field_dict["user_group"] = user_group

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        options = cast(list[str], d.pop("options", UNSET))

        question = d.pop("question", UNSET)

        timeout = d.pop("timeout", UNSET)

        user_group = d.pop("user_group", UNSET)

        get_status_user_prompt = cls(
            guid=guid,
            options=options,
            question=question,
            timeout=timeout,
            user_group=user_group,
        )

        get_status_user_prompt.additional_properties = d
        return get_status_user_prompt

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
