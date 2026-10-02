from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetWifiNetworks")


@_attrs_define
class GetWifiNetworks:
    """
    Attributes:
        connected (bool | Unset): Connected to this network
        guid (str | Unset): The guid of the wifi
        ssid (str | Unset): Ssid of the wlan
        url (str | Unset): The URL of the resource
    """

    connected: bool | Unset = UNSET
    guid: str | Unset = UNSET
    ssid: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connected = self.connected

        guid = self.guid

        ssid = self.ssid

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if connected is not UNSET:
            field_dict["connected"] = connected
        if guid is not UNSET:
            field_dict["guid"] = guid
        if ssid is not UNSET:
            field_dict["ssid"] = ssid
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        connected = d.pop("connected", UNSET)

        guid = d.pop("guid", UNSET)

        ssid = d.pop("ssid", UNSET)

        url = d.pop("url", UNSET)

        get_wifi_networks = cls(
            connected=connected,
            guid=guid,
            ssid=ssid,
            url=url,
        )

        get_wifi_networks.additional_properties = d
        return get_wifi_networks

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
