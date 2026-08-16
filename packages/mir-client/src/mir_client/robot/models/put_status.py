from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.put_status_position import PutStatusPosition


T = TypeVar("T", bound="PutStatus")


@_attrs_define
class PutStatus:
    """
    Attributes:
        answer (str | Unset): Min length: 1, Max length: 255
        clear_error (bool | Unset): Choices are: {True}
        datetime_ (str | Unset):
        guid (str | Unset):
        map_id (str | Unset):
        mode_id (int | Unset): Choices are: {3, 7}
        name (str | Unset): Min length: 1, Max length: 20
        position (PutStatusPosition | Unset):
        prompt_user_group_from_fleet (str | Unset): Min length: 1, Max length: 255
        serial_number (str | Unset):
        state_id (int | Unset): Choices are: {3, 4, 11}, State: {Ready, Pause, Manualcontrol}
        web_session_id (str | Unset):
    """

    answer: str | Unset = UNSET
    clear_error: bool | Unset = UNSET
    datetime_: str | Unset = UNSET
    guid: str | Unset = UNSET
    map_id: str | Unset = UNSET
    mode_id: int | Unset = UNSET
    name: str | Unset = UNSET
    position: PutStatusPosition | Unset = UNSET
    prompt_user_group_from_fleet: str | Unset = UNSET
    serial_number: str | Unset = UNSET
    state_id: int | Unset = UNSET
    web_session_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        answer = self.answer

        clear_error = self.clear_error

        datetime_ = self.datetime_

        guid = self.guid

        map_id = self.map_id

        mode_id = self.mode_id

        name = self.name

        position: dict[str, Any] | Unset = UNSET
        if not isinstance(self.position, Unset):
            position = self.position.to_dict()

        prompt_user_group_from_fleet = self.prompt_user_group_from_fleet

        serial_number = self.serial_number

        state_id = self.state_id

        web_session_id = self.web_session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if answer is not UNSET:
            field_dict["answer"] = answer
        if clear_error is not UNSET:
            field_dict["clear_error"] = clear_error
        if datetime_ is not UNSET:
            field_dict["datetime"] = datetime_
        if guid is not UNSET:
            field_dict["guid"] = guid
        if map_id is not UNSET:
            field_dict["map_id"] = map_id
        if mode_id is not UNSET:
            field_dict["mode_id"] = mode_id
        if name is not UNSET:
            field_dict["name"] = name
        if position is not UNSET:
            field_dict["position"] = position
        if prompt_user_group_from_fleet is not UNSET:
            field_dict["prompt_user_group_from_fleet"] = prompt_user_group_from_fleet
        if serial_number is not UNSET:
            field_dict["serial_number"] = serial_number
        if state_id is not UNSET:
            field_dict["state_id"] = state_id
        if web_session_id is not UNSET:
            field_dict["web_session_id"] = web_session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.put_status_position import PutStatusPosition

        d = dict(src_dict)
        answer = d.pop("answer", UNSET)

        clear_error = d.pop("clear_error", UNSET)

        datetime_ = d.pop("datetime", UNSET)

        guid = d.pop("guid", UNSET)

        map_id = d.pop("map_id", UNSET)

        mode_id = d.pop("mode_id", UNSET)

        name = d.pop("name", UNSET)

        _position = d.pop("position", UNSET)
        position: PutStatusPosition | Unset
        if isinstance(_position, Unset):
            position = UNSET
        else:
            position = PutStatusPosition.from_dict(_position)

        prompt_user_group_from_fleet = d.pop("prompt_user_group_from_fleet", UNSET)

        serial_number = d.pop("serial_number", UNSET)

        state_id = d.pop("state_id", UNSET)

        web_session_id = d.pop("web_session_id", UNSET)

        put_status = cls(
            answer=answer,
            clear_error=clear_error,
            datetime_=datetime_,
            guid=guid,
            map_id=map_id,
            mode_id=mode_id,
            name=name,
            position=position,
            prompt_user_group_from_fleet=prompt_user_group_from_fleet,
            serial_number=serial_number,
            state_id=state_id,
            web_session_id=web_session_id,
        )

        put_status.additional_properties = d
        return put_status

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
