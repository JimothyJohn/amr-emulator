from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_wifi_connections_scan_freqs_item import PostWifiConnectionsScanFreqsItem


T = TypeVar("T", bound="PostWifiConnections")


@_attrs_define
class PostWifiConnections:
    """
    Attributes:
        ssid (str):
        address (str | Unset):
        bgscan_long_interval (int | Unset):
        bgscan_short_interval (int | Unset):
        bgscan_threshold (int | Unset):
        description (str | Unset):
        device (str | Unset):
        dns (str | Unset):
        gateway (str | Unset):
        netmask (str | Unset):
        scan_freqs (list[PostWifiConnectionsScanFreqsItem] | Unset):
        security (str | Unset):
    """

    ssid: str
    address: str | Unset = UNSET
    bgscan_long_interval: int | Unset = UNSET
    bgscan_short_interval: int | Unset = UNSET
    bgscan_threshold: int | Unset = UNSET
    description: str | Unset = UNSET
    device: str | Unset = UNSET
    dns: str | Unset = UNSET
    gateway: str | Unset = UNSET
    netmask: str | Unset = UNSET
    scan_freqs: list[PostWifiConnectionsScanFreqsItem] | Unset = UNSET
    security: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ssid = self.ssid

        address = self.address

        bgscan_long_interval = self.bgscan_long_interval

        bgscan_short_interval = self.bgscan_short_interval

        bgscan_threshold = self.bgscan_threshold

        description = self.description

        device = self.device

        dns = self.dns

        gateway = self.gateway

        netmask = self.netmask

        scan_freqs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.scan_freqs, Unset):
            scan_freqs = []
            for scan_freqs_item_data in self.scan_freqs:
                scan_freqs_item = scan_freqs_item_data.to_dict()
                scan_freqs.append(scan_freqs_item)

        security = self.security

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ssid": ssid,
            }
        )
        if address is not UNSET:
            field_dict["address"] = address
        if bgscan_long_interval is not UNSET:
            field_dict["bgscan_long_interval"] = bgscan_long_interval
        if bgscan_short_interval is not UNSET:
            field_dict["bgscan_short_interval"] = bgscan_short_interval
        if bgscan_threshold is not UNSET:
            field_dict["bgscan_threshold"] = bgscan_threshold
        if description is not UNSET:
            field_dict["description"] = description
        if device is not UNSET:
            field_dict["device"] = device
        if dns is not UNSET:
            field_dict["dns"] = dns
        if gateway is not UNSET:
            field_dict["gateway"] = gateway
        if netmask is not UNSET:
            field_dict["netmask"] = netmask
        if scan_freqs is not UNSET:
            field_dict["scan_freqs"] = scan_freqs
        if security is not UNSET:
            field_dict["security"] = security

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_wifi_connections_scan_freqs_item import PostWifiConnectionsScanFreqsItem

        d = dict(src_dict)
        ssid = d.pop("ssid")

        address = d.pop("address", UNSET)

        bgscan_long_interval = d.pop("bgscan_long_interval", UNSET)

        bgscan_short_interval = d.pop("bgscan_short_interval", UNSET)

        bgscan_threshold = d.pop("bgscan_threshold", UNSET)

        description = d.pop("description", UNSET)

        device = d.pop("device", UNSET)

        dns = d.pop("dns", UNSET)

        gateway = d.pop("gateway", UNSET)

        netmask = d.pop("netmask", UNSET)

        _scan_freqs = d.pop("scan_freqs", UNSET)
        scan_freqs: list[PostWifiConnectionsScanFreqsItem] | Unset = UNSET
        if _scan_freqs is not UNSET:
            scan_freqs = []
            for scan_freqs_item_data in _scan_freqs:
                scan_freqs_item = PostWifiConnectionsScanFreqsItem.from_dict(scan_freqs_item_data)

                scan_freqs.append(scan_freqs_item)

        security = d.pop("security", UNSET)

        post_wifi_connections = cls(
            ssid=ssid,
            address=address,
            bgscan_long_interval=bgscan_long_interval,
            bgscan_short_interval=bgscan_short_interval,
            bgscan_threshold=bgscan_threshold,
            description=description,
            device=device,
            dns=dns,
            gateway=gateway,
            netmask=netmask,
            scan_freqs=scan_freqs,
            security=security,
        )

        post_wifi_connections.additional_properties = d
        return post_wifi_connections

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
