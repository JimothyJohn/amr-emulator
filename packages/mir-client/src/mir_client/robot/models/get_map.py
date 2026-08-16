from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMap")


@_attrs_define
class GetMap:
    """
    Attributes:
        base_map (str | Unset): Base layer
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        guid (str | Unset): The global id unique across robots that identifies this map
        name (str | Unset): The name of the map
        origin_theta (float | Unset): The angle in the map of the center of the map relative to the robots position
        origin_x (float | Unset): The x-coordinate in the map of the center of the map relative to the robots position
        origin_y (float | Unset): The y-coordinate in the map of the center of the map relative to the robots position
        path_guides (str | Unset): The url to the list of path guides in this map
        paths (str | Unset): The url to the list of paths in this map
        positions (str | Unset): The url to the list of positions in this map
        resolution (float | Unset): Deprecated - static resolution is 0.05
        session_id (str | Unset): The global id unique across robots of the area containing this map
    """

    base_map: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    origin_theta: float | Unset = UNSET
    origin_x: float | Unset = UNSET
    origin_y: float | Unset = UNSET
    path_guides: str | Unset = UNSET
    paths: str | Unset = UNSET
    positions: str | Unset = UNSET
    resolution: float | Unset = UNSET
    session_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_map = self.base_map

        created_by = self.created_by

        created_by_id = self.created_by_id

        guid = self.guid

        name = self.name

        origin_theta = self.origin_theta

        origin_x = self.origin_x

        origin_y = self.origin_y

        path_guides = self.path_guides

        paths = self.paths

        positions = self.positions

        resolution = self.resolution

        session_id = self.session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if base_map is not UNSET:
            field_dict["base_map"] = base_map
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if origin_theta is not UNSET:
            field_dict["origin_theta"] = origin_theta
        if origin_x is not UNSET:
            field_dict["origin_x"] = origin_x
        if origin_y is not UNSET:
            field_dict["origin_y"] = origin_y
        if path_guides is not UNSET:
            field_dict["path_guides"] = path_guides
        if paths is not UNSET:
            field_dict["paths"] = paths
        if positions is not UNSET:
            field_dict["positions"] = positions
        if resolution is not UNSET:
            field_dict["resolution"] = resolution
        if session_id is not UNSET:
            field_dict["session_id"] = session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        base_map = d.pop("base_map", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        origin_theta = d.pop("origin_theta", UNSET)

        origin_x = d.pop("origin_x", UNSET)

        origin_y = d.pop("origin_y", UNSET)

        path_guides = d.pop("path_guides", UNSET)

        paths = d.pop("paths", UNSET)

        positions = d.pop("positions", UNSET)

        resolution = d.pop("resolution", UNSET)

        session_id = d.pop("session_id", UNSET)

        get_map = cls(
            base_map=base_map,
            created_by=created_by,
            created_by_id=created_by_id,
            guid=guid,
            name=name,
            origin_theta=origin_theta,
            origin_x=origin_x,
            origin_y=origin_y,
            path_guides=path_guides,
            paths=paths,
            positions=positions,
            resolution=resolution,
            session_id=session_id,
        )

        get_map.additional_properties = d
        return get_map

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
