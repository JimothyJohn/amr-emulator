from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostMapUpload")


@_attrs_define
class PostMapUpload:
    """
    Attributes:
        type_ (str):
        created_by_id (str | Unset):
        guid (str | Unset):
        image_data (str | Unset):
        start_map_guid (str | Unset):
        start_map_theta (float | Unset):
        start_map_x (float | Unset):
        start_map_y (float | Unset):
    """

    type_: str
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    image_data: str | Unset = UNSET
    start_map_guid: str | Unset = UNSET
    start_map_theta: float | Unset = UNSET
    start_map_x: float | Unset = UNSET
    start_map_y: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        created_by_id = self.created_by_id

        guid = self.guid

        image_data = self.image_data

        start_map_guid = self.start_map_guid

        start_map_theta = self.start_map_theta

        start_map_x = self.start_map_x

        start_map_y = self.start_map_y

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if image_data is not UNSET:
            field_dict["image_data"] = image_data
        if start_map_guid is not UNSET:
            field_dict["start_map_guid"] = start_map_guid
        if start_map_theta is not UNSET:
            field_dict["start_map_theta"] = start_map_theta
        if start_map_x is not UNSET:
            field_dict["start_map_x"] = start_map_x
        if start_map_y is not UNSET:
            field_dict["start_map_y"] = start_map_y

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        image_data = d.pop("image_data", UNSET)

        start_map_guid = d.pop("start_map_guid", UNSET)

        start_map_theta = d.pop("start_map_theta", UNSET)

        start_map_x = d.pop("start_map_x", UNSET)

        start_map_y = d.pop("start_map_y", UNSET)

        post_map_upload = cls(
            type_=type_,
            created_by_id=created_by_id,
            guid=guid,
            image_data=image_data,
            start_map_guid=start_map_guid,
            start_map_theta=start_map_theta,
            start_map_x=start_map_x,
            start_map_y=start_map_y,
        )

        post_map_upload.additional_properties = d
        return post_map_upload

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
