from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSetupSerialDevice")


@_attrs_define
class GetSetupSerialDevice:
    """
    Attributes:
        default_value (str | Unset):
        description (str | Unset):
        id (int | Unset):
        name (str | Unset):
        request_succeeded (bool | Unset):
        ros_name (str | Unset):
        url (str | Unset): Specific serial device information
        value (str | Unset):
    """

    default_value: str | Unset = UNSET
    description: str | Unset = UNSET
    id: int | Unset = UNSET
    name: str | Unset = UNSET
    request_succeeded: bool | Unset = UNSET
    ros_name: str | Unset = UNSET
    url: str | Unset = UNSET
    value: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        default_value = self.default_value

        description = self.description

        id = self.id

        name = self.name

        request_succeeded = self.request_succeeded

        ros_name = self.ros_name

        url = self.url

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_value is not UNSET:
            field_dict["default_value"] = default_value
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if request_succeeded is not UNSET:
            field_dict["request_succeeded"] = request_succeeded
        if ros_name is not UNSET:
            field_dict["ros_name"] = ros_name
        if url is not UNSET:
            field_dict["url"] = url
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        default_value = d.pop("default_value", UNSET)

        description = d.pop("description", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        request_succeeded = d.pop("request_succeeded", UNSET)

        ros_name = d.pop("ros_name", UNSET)

        url = d.pop("url", UNSET)

        value = d.pop("value", UNSET)

        get_setup_serial_device = cls(
            default_value=default_value,
            description=description,
            id=id,
            name=name,
            request_succeeded=request_succeeded,
            ros_name=ros_name,
            url=url,
            value=value,
        )

        get_setup_serial_device.additional_properties = d
        return get_setup_serial_device

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
