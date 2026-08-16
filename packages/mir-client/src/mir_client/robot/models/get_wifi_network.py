from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetWifiNetwork")


@_attrs_define
class GetWifiNetwork:
    """
    Attributes:
        channel (int | Unset): Network channel
        connected (bool | Unset): Connected to this network
        device (str | Unset): Device
        frequency (str | Unset): Network frequency
        guid (str | Unset): The guid of the wifi
        security (str | Unset): Security
        ssid (str | Unset): Ssid of the wlan
        strength (int | Unset): Signal strength
        url (str | Unset): Specific wifi network
    """

    channel: int | Unset = UNSET
    connected: bool | Unset = UNSET
    device: str | Unset = UNSET
    frequency: str | Unset = UNSET
    guid: str | Unset = UNSET
    security: str | Unset = UNSET
    ssid: str | Unset = UNSET
    strength: int | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel = self.channel

        connected = self.connected

        device = self.device

        frequency = self.frequency

        guid = self.guid

        security = self.security

        ssid = self.ssid

        strength = self.strength

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if channel is not UNSET:
            field_dict["channel"] = channel
        if connected is not UNSET:
            field_dict["connected"] = connected
        if device is not UNSET:
            field_dict["device"] = device
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if guid is not UNSET:
            field_dict["guid"] = guid
        if security is not UNSET:
            field_dict["security"] = security
        if ssid is not UNSET:
            field_dict["ssid"] = ssid
        if strength is not UNSET:
            field_dict["strength"] = strength
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel = d.pop("channel", UNSET)

        connected = d.pop("connected", UNSET)

        device = d.pop("device", UNSET)

        frequency = d.pop("frequency", UNSET)

        guid = d.pop("guid", UNSET)

        security = d.pop("security", UNSET)

        ssid = d.pop("ssid", UNSET)

        strength = d.pop("strength", UNSET)

        url = d.pop("url", UNSET)

        get_wifi_network = cls(
            channel=channel,
            connected=connected,
            device=device,
            frequency=frequency,
            guid=guid,
            security=security,
            ssid=ssid,
            strength=strength,
            url=url,
        )

        get_wifi_network.additional_properties = d
        return get_wifi_network

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
