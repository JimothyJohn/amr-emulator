from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_path_guide_options_goals_item import GetPathGuideOptionsGoalsItem
    from ..models.get_path_guide_options_starts_item import GetPathGuideOptionsStartsItem
    from ..models.get_path_guide_options_vias_item import GetPathGuideOptionsViasItem


T = TypeVar("T", bound="GetPathGuideOptions")


@_attrs_define
class GetPathGuideOptions:
    """
    Attributes:
        goals (list[GetPathGuideOptionsGoalsItem] | Unset): The list of options for goal positions
        starts (list[GetPathGuideOptionsStartsItem] | Unset): The list of options for start positions
        vias (list[GetPathGuideOptionsViasItem] | Unset): The list of options for via positions
    """

    goals: list[GetPathGuideOptionsGoalsItem] | Unset = UNSET
    starts: list[GetPathGuideOptionsStartsItem] | Unset = UNSET
    vias: list[GetPathGuideOptionsViasItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        goals: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.goals, Unset):
            goals = []
            for goals_item_data in self.goals:
                goals_item = goals_item_data.to_dict()
                goals.append(goals_item)

        starts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.starts, Unset):
            starts = []
            for starts_item_data in self.starts:
                starts_item = starts_item_data.to_dict()
                starts.append(starts_item)

        vias: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.vias, Unset):
            vias = []
            for vias_item_data in self.vias:
                vias_item = vias_item_data.to_dict()
                vias.append(vias_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if goals is not UNSET:
            field_dict["goals"] = goals
        if starts is not UNSET:
            field_dict["starts"] = starts
        if vias is not UNSET:
            field_dict["vias"] = vias

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_path_guide_options_goals_item import GetPathGuideOptionsGoalsItem
        from ..models.get_path_guide_options_starts_item import GetPathGuideOptionsStartsItem
        from ..models.get_path_guide_options_vias_item import GetPathGuideOptionsViasItem

        d = dict(src_dict)
        _goals = d.pop("goals", UNSET)
        goals: list[GetPathGuideOptionsGoalsItem] | Unset = UNSET
        if _goals is not UNSET:
            goals = []
            for goals_item_data in _goals:
                goals_item = GetPathGuideOptionsGoalsItem.from_dict(goals_item_data)

                goals.append(goals_item)

        _starts = d.pop("starts", UNSET)
        starts: list[GetPathGuideOptionsStartsItem] | Unset = UNSET
        if _starts is not UNSET:
            starts = []
            for starts_item_data in _starts:
                starts_item = GetPathGuideOptionsStartsItem.from_dict(starts_item_data)

                starts.append(starts_item)

        _vias = d.pop("vias", UNSET)
        vias: list[GetPathGuideOptionsViasItem] | Unset = UNSET
        if _vias is not UNSET:
            vias = []
            for vias_item_data in _vias:
                vias_item = GetPathGuideOptionsViasItem.from_dict(vias_item_data)

                vias.append(vias_item)

        get_path_guide_options = cls(
            goals=goals,
            starts=starts,
            vias=vias,
        )

        get_path_guide_options.additional_properties = d
        return get_path_guide_options

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
