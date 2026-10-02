from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetWifiConnections")


@_attrs_define
class GetWifiConnections:
    """
    Attributes:
        bssid (str | Unset): Access point mac address
        connected (bool | Unset): Connected to the network of this connection
        mac (str | Unset): Network adapter mac address
        name (str | Unset): Name or id of the connection
        url (str | Unset): The URL of the resource
        uuid (str | Unset): Uuid of the connection
    """

    bssid: str | Unset = UNSET
    connected: bool | Unset = UNSET
    mac: str | Unset = UNSET
    name: str | Unset = UNSET
    url: str | Unset = UNSET
    uuid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bssid = self.bssid

        connected = self.connected

        mac = self.mac

        name = self.name

        url = self.url

        uuid = self.uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bssid is not UNSET:
            field_dict["bssid"] = bssid
        if connected is not UNSET:
            field_dict["connected"] = connected
        if mac is not UNSET:
            field_dict["mac"] = mac
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url
        if uuid is not UNSET:
            field_dict["uuid"] = uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bssid = d.pop("bssid", UNSET)

        connected = d.pop("connected", UNSET)

        mac = d.pop("mac", UNSET)

        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        uuid = d.pop("uuid", UNSET)

        get_wifi_connections = cls(
            bssid=bssid,
            connected=connected,
            mac=mac,
            name=name,
            url=url,
            uuid=uuid,
        )

        get_wifi_connections.additional_properties = d
        return get_wifi_connections

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
