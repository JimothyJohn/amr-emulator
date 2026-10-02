from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutIoModuleStatus")


@_attrs_define
class PutIoModuleStatus:
    """
    Attributes:
        on (bool | Unset):
        port (int | Unset):
        timeout (int | Unset):
    """

    on: bool | Unset = UNSET
    port: int | Unset = UNSET
    timeout: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        on = self.on

        port = self.port

        timeout = self.timeout

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if on is not UNSET:
            field_dict["on"] = on
        if port is not UNSET:
            field_dict["port"] = port
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        on = d.pop("on", UNSET)

        port = d.pop("port", UNSET)

        timeout = d.pop("timeout", UNSET)

        put_io_module_status = cls(
            on=on,
            port=port,
            timeout=timeout,
        )

        put_io_module_status.additional_properties = d
        return put_io_module_status

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
