from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostPathGuidePositions")


@_attrs_define
class PostPathGuidePositions:
    """
    Attributes:
        path_guide_guid (str):
        pos_guid (str):
        pos_type (str):
        guid (str | Unset):
        priority (int | Unset):
    """

    path_guide_guid: str
    pos_guid: str
    pos_type: str
    guid: str | Unset = UNSET
    priority: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path_guide_guid = self.path_guide_guid

        pos_guid = self.pos_guid

        pos_type = self.pos_type

        guid = self.guid

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path_guide_guid": path_guide_guid,
                "pos_guid": pos_guid,
                "pos_type": pos_type,
            }
        )
        if guid is not UNSET:
            field_dict["guid"] = guid
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path_guide_guid = d.pop("path_guide_guid")

        pos_guid = d.pop("pos_guid")

        pos_type = d.pop("pos_type")

        guid = d.pop("guid", UNSET)

        priority = d.pop("priority", UNSET)

        post_path_guide_positions = cls(
            path_guide_guid=path_guide_guid,
            pos_guid=pos_guid,
            pos_type=pos_type,
            guid=guid,
            priority=priority,
        )

        post_path_guide_positions.additional_properties = d
        return post_path_guide_positions

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
