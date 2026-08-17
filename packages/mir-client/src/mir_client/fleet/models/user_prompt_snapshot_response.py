from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_prompt_event import UserPromptEvent


T = TypeVar("T", bound="UserPromptSnapshotResponse")


@_attrs_define
class UserPromptSnapshotResponse:
    """
    Attributes:
        user_prompt_events (list[UserPromptEvent] | Unset):
    """

    user_prompt_events: list[UserPromptEvent] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        user_prompt_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.user_prompt_events, Unset):
            user_prompt_events = []
            for user_prompt_events_item_data in self.user_prompt_events:
                user_prompt_events_item = user_prompt_events_item_data.to_dict()
                user_prompt_events.append(user_prompt_events_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if user_prompt_events is not UNSET:
            field_dict["user-prompt-events"] = user_prompt_events

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_prompt_event import UserPromptEvent

        d = dict(src_dict)
        _user_prompt_events = d.pop("user-prompt-events", UNSET)
        user_prompt_events: list[UserPromptEvent] | Unset = UNSET
        if _user_prompt_events is not UNSET:
            user_prompt_events = []
            for user_prompt_events_item_data in _user_prompt_events:
                user_prompt_events_item = UserPromptEvent.from_dict(user_prompt_events_item_data)

                user_prompt_events.append(user_prompt_events_item)

        user_prompt_snapshot_response = cls(
            user_prompt_events=user_prompt_events,
        )

        return user_prompt_snapshot_response
