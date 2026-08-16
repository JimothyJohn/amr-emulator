from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetFootprint")


@_attrs_define
class GetFootprint:
    """
    Attributes:
        config_id (str | Unset): The model name of the product for which the footprint is created
        created_by_id (str | Unset): The global id of the user who created this entry
        custom (bool | Unset): Custom or rectangular footprint
        footprint_points (str | Unset): The string defining the points in xy of the footprint
        guid (str | Unset): The global id unique across robots that identifies this cart type
        height (float | Unset): The height of this footprint
        hook (bool | Unset): If the footprint is for a hook or not
        name (str | Unset): The name of the footprint type
    """

    config_id: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    custom: bool | Unset = UNSET
    footprint_points: str | Unset = UNSET
    guid: str | Unset = UNSET
    height: float | Unset = UNSET
    hook: bool | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config_id = self.config_id

        created_by_id = self.created_by_id

        custom = self.custom

        footprint_points = self.footprint_points

        guid = self.guid

        height = self.height

        hook = self.hook

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config_id is not UNSET:
            field_dict["config_id"] = config_id
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if custom is not UNSET:
            field_dict["custom"] = custom
        if footprint_points is not UNSET:
            field_dict["footprint_points"] = footprint_points
        if guid is not UNSET:
            field_dict["guid"] = guid
        if height is not UNSET:
            field_dict["height"] = height
        if hook is not UNSET:
            field_dict["hook"] = hook
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        config_id = d.pop("config_id", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        custom = d.pop("custom", UNSET)

        footprint_points = d.pop("footprint_points", UNSET)

        guid = d.pop("guid", UNSET)

        height = d.pop("height", UNSET)

        hook = d.pop("hook", UNSET)

        name = d.pop("name", UNSET)

        get_footprint = cls(
            config_id=config_id,
            created_by_id=created_by_id,
            custom=custom,
            footprint_points=footprint_points,
            guid=guid,
            height=height,
            hook=hook,
            name=name,
        )

        get_footprint.additional_properties = d
        return get_footprint

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
