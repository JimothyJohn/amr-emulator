from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSoftwareLog")


@_attrs_define
class GetSoftwareLog:
    """
    Attributes:
        action (str | Unset): The action performed (upgrade/restore)
        end_time (datetime.datetime | Unset): The end time of the upgrade
        from_ (str | Unset): The software version upgrading from
        guid (str | Unset): The guid of upgrade entry
        message (str | Unset): The status message from upgrade
        start_time (datetime.datetime | Unset): The start time of the upgrade
        state (str | Unset): The state of the upgrade (succeeded/failed/started
        to (str | Unset): The software version upgrading to
    """

    action: str | Unset = UNSET
    end_time: datetime.datetime | Unset = UNSET
    from_: str | Unset = UNSET
    guid: str | Unset = UNSET
    message: str | Unset = UNSET
    start_time: datetime.datetime | Unset = UNSET
    state: str | Unset = UNSET
    to: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action

        end_time: str | Unset = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        from_ = self.from_

        guid = self.guid

        message = self.message

        start_time: str | Unset = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        state = self.state

        to = self.to

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action is not UNSET:
            field_dict["action"] = action
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if from_ is not UNSET:
            field_dict["from"] = from_
        if guid is not UNSET:
            field_dict["guid"] = guid
        if message is not UNSET:
            field_dict["message"] = message
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if state is not UNSET:
            field_dict["state"] = state
        if to is not UNSET:
            field_dict["to"] = to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action = d.pop("action", UNSET)

        _end_time = d.pop("end_time", UNSET)
        end_time: datetime.datetime | Unset
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = datetime.datetime.fromisoformat(_end_time)

        from_ = d.pop("from", UNSET)

        guid = d.pop("guid", UNSET)

        message = d.pop("message", UNSET)

        _start_time = d.pop("start_time", UNSET)
        start_time: datetime.datetime | Unset
        if isinstance(_start_time, Unset):
            start_time = UNSET
        else:
            start_time = datetime.datetime.fromisoformat(_start_time)

        state = d.pop("state", UNSET)

        to = d.pop("to", UNSET)

        get_software_log = cls(
            action=action,
            end_time=end_time,
            from_=from_,
            guid=guid,
            message=message,
            start_time=start_time,
            state=state,
            to=to,
        )

        get_software_log.additional_properties = d
        return get_software_log

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
