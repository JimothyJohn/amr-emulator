from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPathGuideOptionsGoalsItem")


@_attrs_define
class GetPathGuideOptionsGoalsItem:
    """
    Attributes:
        name (str | Unset): The name of the position
        pos_guid (str | Unset): The global unique id across robots that identifies this position
    """

    name: str | Unset = UNSET
    pos_guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        pos_guid = self.pos_guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if pos_guid is not UNSET:
            field_dict["pos_guid"] = pos_guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        pos_guid = d.pop("pos_guid", UNSET)

        get_path_guide_options_goals_item = cls(
            name=name,
            pos_guid=pos_guid,
        )

        get_path_guide_options_goals_item.additional_properties = d
        return get_path_guide_options_goals_item

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
