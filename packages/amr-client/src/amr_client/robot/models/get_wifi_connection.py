from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetWifiConnection")


@_attrs_define
class GetWifiConnection:
    """
    Attributes:
        bgscan_long_interval (int | Unset): Bgscan lang interval parameter
        bgscan_short_interval (int | Unset): Bgscan short interval parameter
        bgscan_threshold (int | Unset): Bgscan threshold parameter
        broadcast (str | Unset): Broadcast for the connection
        bssid (str | Unset): Access point mac address
        connected (bool | Unset): Connected to the network of this connection
        description (str | Unset): Description of the connection
        device (str | Unset): Device to use for this connection
        dns (str | Unset): Dnss for the connection
        ip_address (str | Unset): Ip address for the connection
        last_connected (str | Unset): Date and time for when the connection was last successfully connected
        mac (str | Unset): Network adapter mac address
        name (str | Unset): Name or id of the connection
        netmask (str | Unset): Netmask for the connection
        scan_freqs (list[int] | Unset): A list of scan frequecies
        security (str | Unset): The security method used by the connection
        type_ (str | Unset): Connection type e.g. 802-11-wireless
        url (str | Unset): Specific connection
        uuid (str | Unset): Uuid of the connection
    """

    bgscan_long_interval: int | Unset = UNSET
    bgscan_short_interval: int | Unset = UNSET
    bgscan_threshold: int | Unset = UNSET
    broadcast: str | Unset = UNSET
    bssid: str | Unset = UNSET
    connected: bool | Unset = UNSET
    description: str | Unset = UNSET
    device: str | Unset = UNSET
    dns: str | Unset = UNSET
    ip_address: str | Unset = UNSET
    last_connected: str | Unset = UNSET
    mac: str | Unset = UNSET
    name: str | Unset = UNSET
    netmask: str | Unset = UNSET
    scan_freqs: list[int] | Unset = UNSET
    security: str | Unset = UNSET
    type_: str | Unset = UNSET
    url: str | Unset = UNSET
    uuid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bgscan_long_interval = self.bgscan_long_interval

        bgscan_short_interval = self.bgscan_short_interval

        bgscan_threshold = self.bgscan_threshold

        broadcast = self.broadcast

        bssid = self.bssid

        connected = self.connected

        description = self.description

        device = self.device

        dns = self.dns

        ip_address = self.ip_address

        last_connected = self.last_connected

        mac = self.mac

        name = self.name

        netmask = self.netmask

        scan_freqs: list[int] | Unset = UNSET
        if not isinstance(self.scan_freqs, Unset):
            scan_freqs = self.scan_freqs

        security = self.security

        type_ = self.type_

        url = self.url

        uuid = self.uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bgscan_long_interval is not UNSET:
            field_dict["bgscan_long_interval"] = bgscan_long_interval
        if bgscan_short_interval is not UNSET:
            field_dict["bgscan_short_interval"] = bgscan_short_interval
        if bgscan_threshold is not UNSET:
            field_dict["bgscan_threshold"] = bgscan_threshold
        if broadcast is not UNSET:
            field_dict["broadcast"] = broadcast
        if bssid is not UNSET:
            field_dict["bssid"] = bssid
        if connected is not UNSET:
            field_dict["connected"] = connected
        if description is not UNSET:
            field_dict["description"] = description
        if device is not UNSET:
            field_dict["device"] = device
        if dns is not UNSET:
            field_dict["dns"] = dns
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if last_connected is not UNSET:
            field_dict["last_connected"] = last_connected
        if mac is not UNSET:
            field_dict["mac"] = mac
        if name is not UNSET:
            field_dict["name"] = name
        if netmask is not UNSET:
            field_dict["netmask"] = netmask
        if scan_freqs is not UNSET:
            field_dict["scan_freqs"] = scan_freqs
        if security is not UNSET:
            field_dict["security"] = security
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if uuid is not UNSET:
            field_dict["uuid"] = uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bgscan_long_interval = d.pop("bgscan_long_interval", UNSET)

        bgscan_short_interval = d.pop("bgscan_short_interval", UNSET)

        bgscan_threshold = d.pop("bgscan_threshold", UNSET)

        broadcast = d.pop("broadcast", UNSET)

        bssid = d.pop("bssid", UNSET)

        connected = d.pop("connected", UNSET)

        description = d.pop("description", UNSET)

        device = d.pop("device", UNSET)

        dns = d.pop("dns", UNSET)

        ip_address = d.pop("ip_address", UNSET)

        last_connected = d.pop("last_connected", UNSET)

        mac = d.pop("mac", UNSET)

        name = d.pop("name", UNSET)

        netmask = d.pop("netmask", UNSET)

        scan_freqs = cast(list[int], d.pop("scan_freqs", UNSET))

        security = d.pop("security", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        uuid = d.pop("uuid", UNSET)

        get_wifi_connection = cls(
            bgscan_long_interval=bgscan_long_interval,
            bgscan_short_interval=bgscan_short_interval,
            bgscan_threshold=bgscan_threshold,
            broadcast=broadcast,
            bssid=bssid,
            connected=connected,
            description=description,
            device=device,
            dns=dns,
            ip_address=ip_address,
            last_connected=last_connected,
            mac=mac,
            name=name,
            netmask=netmask,
            scan_freqs=scan_freqs,
            security=security,
            type_=type_,
            url=url,
            uuid=uuid,
        )

        get_wifi_connection.additional_properties = d
        return get_wifi_connection

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
