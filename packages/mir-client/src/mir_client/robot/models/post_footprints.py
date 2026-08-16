from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostFootprints")


@_attrs_define
class PostFootprints:
    """
    Attributes:
        config_id (str):
        footprint_points (str):
        height (float):
        hook (bool):
        name (str): Min length: 1, Max length: 255
        created_by_id (str | Unset):
        guid (str | Unset):
    """

    config_id: str
    footprint_points: str
    height: float
    hook: bool
    name: str
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config_id = self.config_id

        footprint_points = self.footprint_points

        height = self.height

        hook = self.hook

        name = self.name

        created_by_id = self.created_by_id

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config_id": config_id,
                "footprint_points": footprint_points,
                "height": height,
                "hook": hook,
                "name": name,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        config_id = d.pop("config_id")

        footprint_points = d.pop("footprint_points")

        height = d.pop("height")

        hook = d.pop("hook")

        name = d.pop("name")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        post_footprints = cls(
            config_id=config_id,
            footprint_points=footprint_points,
            height=height,
            hook=hook,
            name=name,
            created_by_id=created_by_id,
            guid=guid,
        )

        post_footprints.additional_properties = d
        return post_footprints

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
