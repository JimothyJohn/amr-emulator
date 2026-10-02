from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.action_status import ActionStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrderAction")


@_attrs_define
class OrderAction:
    """
    Attributes:
        action_id (int | None | Unset):
        action_type (None | str | Unset):
        action_status (ActionStatus | Unset):
        action_text (None | str | Unset):
        action_start_time (datetime.datetime | None | Unset):
        action_end_time (datetime.datetime | None | Unset):
        action_duration (None | str | Unset):
    """

    action_id: int | None | Unset = UNSET
    action_type: None | str | Unset = UNSET
    action_status: ActionStatus | Unset = UNSET
    action_text: None | str | Unset = UNSET
    action_start_time: datetime.datetime | None | Unset = UNSET
    action_end_time: datetime.datetime | None | Unset = UNSET
    action_duration: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        action_id: int | None | Unset
        if isinstance(self.action_id, Unset):
            action_id = UNSET
        else:
            action_id = self.action_id

        action_type: None | str | Unset
        if isinstance(self.action_type, Unset):
            action_type = UNSET
        else:
            action_type = self.action_type

        action_status: str | Unset = UNSET
        if not isinstance(self.action_status, Unset):
            action_status = self.action_status.value

        action_text: None | str | Unset
        if isinstance(self.action_text, Unset):
            action_text = UNSET
        else:
            action_text = self.action_text

        action_start_time: None | str | Unset
        if isinstance(self.action_start_time, Unset):
            action_start_time = UNSET
        elif isinstance(self.action_start_time, datetime.datetime):
            action_start_time = self.action_start_time.isoformat()
        else:
            action_start_time = self.action_start_time

        action_end_time: None | str | Unset
        if isinstance(self.action_end_time, Unset):
            action_end_time = UNSET
        elif isinstance(self.action_end_time, datetime.datetime):
            action_end_time = self.action_end_time.isoformat()
        else:
            action_end_time = self.action_end_time

        action_duration: None | str | Unset
        if isinstance(self.action_duration, Unset):
            action_duration = UNSET
        else:
            action_duration = self.action_duration

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if action_id is not UNSET:
            field_dict["action-id"] = action_id
        if action_type is not UNSET:
            field_dict["action-type"] = action_type
        if action_status is not UNSET:
            field_dict["action-status"] = action_status
        if action_text is not UNSET:
            field_dict["action-text"] = action_text
        if action_start_time is not UNSET:
            field_dict["action-start-time"] = action_start_time
        if action_end_time is not UNSET:
            field_dict["action-end-time"] = action_end_time
        if action_duration is not UNSET:
            field_dict["action-duration"] = action_duration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_action_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        action_id = _parse_action_id(d.pop("action-id", UNSET))

        def _parse_action_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action_type = _parse_action_type(d.pop("action-type", UNSET))

        _action_status = d.pop("action-status", UNSET)
        action_status: ActionStatus | Unset
        if isinstance(_action_status, Unset):
            action_status = UNSET
        else:
            action_status = ActionStatus(_action_status)

        def _parse_action_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action_text = _parse_action_text(d.pop("action-text", UNSET))

        def _parse_action_start_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                action_start_time_type_0 = datetime.datetime.fromisoformat(data)

                return action_start_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        action_start_time = _parse_action_start_time(d.pop("action-start-time", UNSET))

        def _parse_action_end_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                action_end_time_type_0 = datetime.datetime.fromisoformat(data)

                return action_end_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        action_end_time = _parse_action_end_time(d.pop("action-end-time", UNSET))

        def _parse_action_duration(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action_duration = _parse_action_duration(d.pop("action-duration", UNSET))

        order_action = cls(
            action_id=action_id,
            action_type=action_type,
            action_status=action_status,
            action_text=action_text,
            action_start_time=action_start_time,
            action_end_time=action_end_time,
            action_duration=action_duration,
        )

        return order_action
