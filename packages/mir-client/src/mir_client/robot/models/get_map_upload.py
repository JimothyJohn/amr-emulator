from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMapUpload")


@_attrs_define
class GetMapUpload:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global guid of this map upload
        id (int | Unset):
        image_data (str | Unset):
        start_map_guid (str | Unset):
        start_map_theta (float | Unset):
        start_map_x (float | Unset):
        start_map_y (float | Unset):
        state (str | Unset):
        type_ (str | Unset):
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    id: int | Unset = UNSET
    image_data: str | Unset = UNSET
    start_map_guid: str | Unset = UNSET
    start_map_theta: float | Unset = UNSET
    start_map_x: float | Unset = UNSET
    start_map_y: float | Unset = UNSET
    state: str | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        id = self.id

        image_data = self.image_data

        start_map_guid = self.start_map_guid

        start_map_theta = self.start_map_theta

        start_map_x = self.start_map_x

        start_map_y = self.start_map_y

        state = self.state

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if id is not UNSET:
            field_dict["id"] = id
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
        if state is not UNSET:
            field_dict["state"] = state
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        id = d.pop("id", UNSET)

        image_data = d.pop("image_data", UNSET)

        start_map_guid = d.pop("start_map_guid", UNSET)

        start_map_theta = d.pop("start_map_theta", UNSET)

        start_map_x = d.pop("start_map_x", UNSET)

        start_map_y = d.pop("start_map_y", UNSET)

        state = d.pop("state", UNSET)

        type_ = d.pop("type", UNSET)

        get_map_upload = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            id=id,
            image_data=image_data,
            start_map_guid=start_map_guid,
            start_map_theta=start_map_theta,
            start_map_x=start_map_x,
            start_map_y=start_map_y,
            state=state,
            type_=type_,
        )

        get_map_upload.additional_properties = d
        return get_map_upload

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
