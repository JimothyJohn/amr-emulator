from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostElevators")


@_attrs_define
class PostElevators:
    """
    Attributes:
        driver (str):
        ip (str):
        name (str):
        session_guid (str):
        active (bool | Unset):
        authentication (str | Unset):
        created_by_id (str | Unset):
        elevator_namespace (str | Unset):
        guid (str | Unset):
        one_way (int | Unset):
        password (str | Unset):
        port (int | Unset):
        security_policy (str | Unset):
        turn_in_place (bool | Unset):
        username (str | Unset):
    """

    driver: str
    ip: str
    name: str
    session_guid: str
    active: bool | Unset = UNSET
    authentication: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    elevator_namespace: str | Unset = UNSET
    guid: str | Unset = UNSET
    one_way: int | Unset = UNSET
    password: str | Unset = UNSET
    port: int | Unset = UNSET
    security_policy: str | Unset = UNSET
    turn_in_place: bool | Unset = UNSET
    username: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        driver = self.driver

        ip = self.ip

        name = self.name

        session_guid = self.session_guid

        active = self.active

        authentication = self.authentication

        created_by_id = self.created_by_id

        elevator_namespace = self.elevator_namespace

        guid = self.guid

        one_way = self.one_way

        password = self.password

        port = self.port

        security_policy = self.security_policy

        turn_in_place = self.turn_in_place

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "driver": driver,
                "ip": ip,
                "name": name,
                "session_guid": session_guid,
            }
        )
        if active is not UNSET:
            field_dict["active"] = active
        if authentication is not UNSET:
            field_dict["authentication"] = authentication
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if elevator_namespace is not UNSET:
            field_dict["elevator_namespace"] = elevator_namespace
        if guid is not UNSET:
            field_dict["guid"] = guid
        if one_way is not UNSET:
            field_dict["one_way"] = one_way
        if password is not UNSET:
            field_dict["password"] = password
        if port is not UNSET:
            field_dict["port"] = port
        if security_policy is not UNSET:
            field_dict["security_policy"] = security_policy
        if turn_in_place is not UNSET:
            field_dict["turn_in_place"] = turn_in_place
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        driver = d.pop("driver")

        ip = d.pop("ip")

        name = d.pop("name")

        session_guid = d.pop("session_guid")

        active = d.pop("active", UNSET)

        authentication = d.pop("authentication", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        elevator_namespace = d.pop("elevator_namespace", UNSET)

        guid = d.pop("guid", UNSET)

        one_way = d.pop("one_way", UNSET)

        password = d.pop("password", UNSET)

        port = d.pop("port", UNSET)

        security_policy = d.pop("security_policy", UNSET)

        turn_in_place = d.pop("turn_in_place", UNSET)

        username = d.pop("username", UNSET)

        post_elevators = cls(
            driver=driver,
            ip=ip,
            name=name,
            session_guid=session_guid,
            active=active,
            authentication=authentication,
            created_by_id=created_by_id,
            elevator_namespace=elevator_namespace,
            guid=guid,
            one_way=one_way,
            password=password,
            port=port,
            security_policy=security_policy,
            turn_in_place=turn_in_place,
            username=username,
        )

        post_elevators.additional_properties = d
        return post_elevators

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
