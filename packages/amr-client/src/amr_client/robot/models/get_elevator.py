from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetElevator")


@_attrs_define
class GetElevator:
    """
    Attributes:
        active (bool | Unset): Boolean indicating the state of the elevator
        authentication (str | Unset): Authentication type for the opcua server
        created_by (str | Unset): The url to the description of this elevator
        created_by_id (str | Unset): The global id of the user who created this entry
        driver (str | Unset): Driver used to connect to the elevator server
        elevator_namespace (str | Unset): Namespace under which the elevator is available on the opcua server
        guid (str | Unset): The global id unique across robots that identifies this elevator
        ip (str | Unset): The ip of the elevator
        name (str | Unset): The name of the elevator
        one_way (int | Unset): Integer indicating, if the elevator is one_way only, and in which direction
        password (str | Unset): Password for the opcua server
        port (int | Unset): Port on which the serer ir running
        security_policy (str | Unset): Security policy type for the opcua server
        session_guid (str | Unset): The global id unique across robots containing this elevator
        turn_in_place (bool | Unset): Boolean indicating if the robot can turn in the elevator
        username (str | Unset): Username for the opcua server
    """

    active: bool | Unset = UNSET
    authentication: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    driver: str | Unset = UNSET
    elevator_namespace: str | Unset = UNSET
    guid: str | Unset = UNSET
    ip: str | Unset = UNSET
    name: str | Unset = UNSET
    one_way: int | Unset = UNSET
    password: str | Unset = UNSET
    port: int | Unset = UNSET
    security_policy: str | Unset = UNSET
    session_guid: str | Unset = UNSET
    turn_in_place: bool | Unset = UNSET
    username: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active = self.active

        authentication = self.authentication

        created_by = self.created_by

        created_by_id = self.created_by_id

        driver = self.driver

        elevator_namespace = self.elevator_namespace

        guid = self.guid

        ip = self.ip

        name = self.name

        one_way = self.one_way

        password = self.password

        port = self.port

        security_policy = self.security_policy

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
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if driver is not UNSET:
            field_dict["driver"] = driver
        if elevator_namespace is not UNSET:
            field_dict["elevator_namespace"] = elevator_namespace
        if guid is not UNSET:
            field_dict["guid"] = guid
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
        if security_policy is not UNSET:
            field_dict["security_policy"] = security_policy
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

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        driver = d.pop("driver", UNSET)

        elevator_namespace = d.pop("elevator_namespace", UNSET)

        guid = d.pop("guid", UNSET)

        ip = d.pop("ip", UNSET)

        name = d.pop("name", UNSET)

        one_way = d.pop("one_way", UNSET)

        password = d.pop("password", UNSET)

        port = d.pop("port", UNSET)

        security_policy = d.pop("security_policy", UNSET)

        session_guid = d.pop("session_guid", UNSET)

        turn_in_place = d.pop("turn_in_place", UNSET)

        username = d.pop("username", UNSET)

        get_elevator = cls(
            active=active,
            authentication=authentication,
            created_by=created_by,
            created_by_id=created_by_id,
            driver=driver,
            elevator_namespace=elevator_namespace,
            guid=guid,
            ip=ip,
            name=name,
            one_way=one_way,
            password=password,
            port=port,
            security_policy=security_policy,
            session_guid=session_guid,
            turn_in_place=turn_in_place,
            username=username,
        )

        get_elevator.additional_properties = d
        return get_elevator

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
