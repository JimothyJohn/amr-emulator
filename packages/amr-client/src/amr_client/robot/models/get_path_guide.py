from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPathGuide")


@_attrs_define
class GetPathGuide:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this element
        created_by_id (str | Unset): The global unique id of the user that created this path guide
        goals_count (int | Unset): The number of goal positions in the path guide
        guid (str | Unset): The global unique id across robots that identifies this path guide
        map_id (str | Unset): The global id of the map this path guide belongs to
        name (str | Unset): The name of the path guide
        options (str | Unset): The url to the list of position options for this path path
        positions (str | Unset): The url to the list of positions used in this path guide
        starts_count (int | Unset): The number of start positions in the path guide
        vias_count (int | Unset): The number of via positions in the path guide
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    goals_count: int | Unset = UNSET
    guid: str | Unset = UNSET
    map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    options: str | Unset = UNSET
    positions: str | Unset = UNSET
    starts_count: int | Unset = UNSET
    vias_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        goals_count = self.goals_count

        guid = self.guid

        map_id = self.map_id

        name = self.name

        options = self.options

        positions = self.positions

        starts_count = self.starts_count

        vias_count = self.vias_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if goals_count is not UNSET:
            field_dict["goals_count"] = goals_count
        if guid is not UNSET:
            field_dict["guid"] = guid
        if map_id is not UNSET:
            field_dict["map_id"] = map_id
        if name is not UNSET:
            field_dict["name"] = name
        if options is not UNSET:
            field_dict["options"] = options
        if positions is not UNSET:
            field_dict["positions"] = positions
        if starts_count is not UNSET:
            field_dict["starts_count"] = starts_count
        if vias_count is not UNSET:
            field_dict["vias_count"] = vias_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        goals_count = d.pop("goals_count", UNSET)

        guid = d.pop("guid", UNSET)

        map_id = d.pop("map_id", UNSET)

        name = d.pop("name", UNSET)

        options = d.pop("options", UNSET)

        positions = d.pop("positions", UNSET)

        starts_count = d.pop("starts_count", UNSET)

        vias_count = d.pop("vias_count", UNSET)

        get_path_guide = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            goals_count=goals_count,
            guid=guid,
            map_id=map_id,
            name=name,
            options=options,
            positions=positions,
            starts_count=starts_count,
            vias_count=vias_count,
        )

        get_path_guide.additional_properties = d
        return get_path_guide

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
