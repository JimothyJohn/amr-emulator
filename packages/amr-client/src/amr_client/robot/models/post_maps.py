from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostMaps")


@_attrs_define
class PostMaps:
    """
    Attributes:
        name (str): Min length: 1, Max length: 40
        origin_theta (float):
        origin_x (float):
        origin_y (float):
        session_id (str):
        base_map (str | Unset):
        created_by_id (str | Unset):
        guid (str | Unset):
        resolution (float | Unset):
    """

    name: str
    origin_theta: float
    origin_x: float
    origin_y: float
    session_id: str
    base_map: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    resolution: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        origin_theta = self.origin_theta

        origin_x = self.origin_x

        origin_y = self.origin_y

        session_id = self.session_id

        base_map = self.base_map

        created_by_id = self.created_by_id

        guid = self.guid

        resolution = self.resolution

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "origin_theta": origin_theta,
                "origin_x": origin_x,
                "origin_y": origin_y,
                "session_id": session_id,
            }
        )
        if base_map is not UNSET:
            field_dict["base_map"] = base_map
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if resolution is not UNSET:
            field_dict["resolution"] = resolution

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        origin_theta = d.pop("origin_theta")

        origin_x = d.pop("origin_x")

        origin_y = d.pop("origin_y")

        session_id = d.pop("session_id")

        base_map = d.pop("base_map", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        resolution = d.pop("resolution", UNSET)

        post_maps = cls(
            name=name,
            origin_theta=origin_theta,
            origin_x=origin_x,
            origin_y=origin_y,
            session_id=session_id,
            base_map=base_map,
            created_by_id=created_by_id,
            guid=guid,
            resolution=resolution,
        )

        post_maps.additional_properties = d
        return post_maps

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
