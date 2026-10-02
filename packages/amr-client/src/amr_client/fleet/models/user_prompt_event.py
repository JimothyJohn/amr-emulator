from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserPromptEvent")


@_attrs_define
class UserPromptEvent:
    """
    Attributes:
        id (str | Unset):
        title (str | Unset):
        options (list[str] | Unset):
        roles (list[str] | Unset):
        timeout (int | Unset):
        timestamp (datetime.datetime | Unset):
        serial_order_id (str | Unset):
        robot_id (str | Unset):
    """

    id: str | Unset = UNSET
    title: str | Unset = UNSET
    options: list[str] | Unset = UNSET
    roles: list[str] | Unset = UNSET
    timeout: int | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    serial_order_id: str | Unset = UNSET
    robot_id: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        options: list[str] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options

        roles: list[str] | Unset = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        timeout = self.timeout

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        serial_order_id = self.serial_order_id

        robot_id = self.robot_id

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if options is not UNSET:
            field_dict["options"] = options
        if roles is not UNSET:
            field_dict["roles"] = roles
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if serial_order_id is not UNSET:
            field_dict["serial-order-id"] = serial_order_id
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        options = cast(list[str], d.pop("options", UNSET))

        roles = cast(list[str], d.pop("roles", UNSET))

        timeout = d.pop("timeout", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = datetime.datetime.fromisoformat(_timestamp)

        serial_order_id = d.pop("serial-order-id", UNSET)

        robot_id = d.pop("robot-id", UNSET)

        user_prompt_event = cls(
            id=id,
            title=title,
            options=options,
            roles=roles,
            timeout=timeout,
            timestamp=timestamp,
            serial_order_id=serial_order_id,
            robot_id=robot_id,
        )

        return user_prompt_event
