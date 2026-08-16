from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPathGuidesPosition")


@_attrs_define
class GetPathGuidesPosition:
    """
    Attributes:
        guid (str | Unset): The global unique id across robots of the position in the list of path constraints positions
        path_guide_guid (str | Unset): The global unique id across robots of the path guide this position is related to
        pos_guid (str | Unset): The global unique id across robots that identifies this position
        pos_type (str | Unset): The type of position of the guide (start/via/goal)
        priority (int | Unset): The order in which to follow the via positions in the path guide
    """

    guid: str | Unset = UNSET
    path_guide_guid: str | Unset = UNSET
    pos_guid: str | Unset = UNSET
    pos_type: str | Unset = UNSET
    priority: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        path_guide_guid = self.path_guide_guid

        pos_guid = self.pos_guid

        pos_type = self.pos_type

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if path_guide_guid is not UNSET:
            field_dict["path_guide_guid"] = path_guide_guid
        if pos_guid is not UNSET:
            field_dict["pos_guid"] = pos_guid
        if pos_type is not UNSET:
            field_dict["pos_type"] = pos_type
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        path_guide_guid = d.pop("path_guide_guid", UNSET)

        pos_guid = d.pop("pos_guid", UNSET)

        pos_type = d.pop("pos_type", UNSET)

        priority = d.pop("priority", UNSET)

        get_path_guides_position = cls(
            guid=guid,
            path_guide_guid=path_guide_guid,
            pos_guid=pos_guid,
            pos_type=pos_type,
            priority=priority,
        )

        get_path_guides_position.additional_properties = d
        return get_path_guides_position

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
