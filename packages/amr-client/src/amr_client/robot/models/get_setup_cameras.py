from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSetupCameras")


@_attrs_define
class GetSetupCameras:
    """
    Attributes:
        camera_model (str | Unset):
        camera_position (str | Unset):
        url (str | Unset): The URL of the resource
        value (str | Unset):
    """

    camera_model: str | Unset = UNSET
    camera_position: str | Unset = UNSET
    url: str | Unset = UNSET
    value: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        camera_model = self.camera_model

        camera_position = self.camera_position

        url = self.url

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if camera_model is not UNSET:
            field_dict["camera_model"] = camera_model
        if camera_position is not UNSET:
            field_dict["camera_position"] = camera_position
        if url is not UNSET:
            field_dict["url"] = url
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        camera_model = d.pop("camera_model", UNSET)

        camera_position = d.pop("camera_position", UNSET)

        url = d.pop("url", UNSET)

        value = d.pop("value", UNSET)

        get_setup_cameras = cls(
            camera_model=camera_model,
            camera_position=camera_position,
            url=url,
            value=value,
        )

        get_setup_cameras.additional_properties = d
        return get_setup_cameras

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
