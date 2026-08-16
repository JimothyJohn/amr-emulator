from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutElevator")


@_attrs_define
class PutElevator:
    """
    Attributes:
        active (bool | Unset):
        authentication (str | Unset): Choices are: {"Anonymous", "Username", "Certificate"}
        driver (str | Unset): Choices are: {"Hitachi", "OPC_UA"}
        elevator_namespace (str | Unset):
        ip (str | Unset):
        name (str | Unset):
        one_way (int | Unset):
        password (str | Unset):
        port (int | Unset):
        session_guid (str | Unset):
        turn_in_place (bool | Unset):
        username (str | Unset):
    """

    active: bool | Unset = UNSET
    authentication: str | Unset = UNSET
    driver: str | Unset = UNSET
    elevator_namespace: str | Unset = UNSET
    ip: str | Unset = UNSET
    name: str | Unset = UNSET
    one_way: int | Unset = UNSET
    password: str | Unset = UNSET
    port: int | Unset = UNSET
    session_guid: str | Unset = UNSET
    turn_in_place: bool | Unset = UNSET
    username: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active = self.active

        authentication = self.authentication

        driver = self.driver

        elevator_namespace = self.elevator_namespace

        ip = self.ip

        name = self.name

        one_way = self.one_way

        password = self.password

        port = self.port

        session_guid = self.session_guid

        turn_in_place = self.turn_in_place

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active is not UNSET:
            field_dict["active"] = active
        if authentication is not UNSET:
            field_dict["authentication"] = authentication
        if driver is not UNSET:
            field_dict["driver"] = driver
        if elevator_namespace is not UNSET:
            field_dict["elevator_namespace"] = elevator_namespace
        if ip is not UNSET:
            field_dict["ip"] = ip
        if name is not UNSET:
            field_dict["name"] = name
        if one_way is not UNSET:
            field_dict["one_way"] = one_way
        if password is not UNSET:
            field_dict["password"] = password
        if port is not UNSET:
            field_dict["port"] = port
        if session_guid is not UNSET:
            field_dict["session_guid"] = session_guid
        if turn_in_place is not UNSET:
            field_dict["turn_in_place"] = turn_in_place
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        active = d.pop("active", UNSET)

        authentication = d.pop("authentication", UNSET)

        driver = d.pop("driver", UNSET)

        elevator_namespace = d.pop("elevator_namespace", UNSET)

        ip = d.pop("ip", UNSET)

        name = d.pop("name", UNSET)

        one_way = d.pop("one_way", UNSET)

        password = d.pop("password", UNSET)

        port = d.pop("port", UNSET)

        session_guid = d.pop("session_guid", UNSET)

        turn_in_place = d.pop("turn_in_place", UNSET)

        username = d.pop("username", UNSET)

        put_elevator = cls(
            active=active,
            authentication=authentication,
            driver=driver,
            elevator_namespace=elevator_namespace,
            ip=ip,
            name=name,
            one_way=one_way,
            password=password,
            port=port,
            session_guid=session_guid,
            turn_in_place=turn_in_place,
            username=username,
        )

        put_elevator.additional_properties = d
        return put_elevator

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
