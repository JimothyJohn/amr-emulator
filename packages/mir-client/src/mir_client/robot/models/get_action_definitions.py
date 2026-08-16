from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_action_definitions_descriptions_item import (
        GetActionDefinitionsDescriptionsItem,
    )
    from ..models.get_action_definitions_parameters_item import GetActionDefinitionsParametersItem


T = TypeVar("T", bound="GetActionDefinitions")


@_attrs_define
class GetActionDefinitions:
    """
    Attributes:
        action_type (str | Unset):
        description (str | Unset):
        descriptions (list[GetActionDefinitionsDescriptionsItem] | Unset):
        help_ (str | Unset):
        mission_group_id (str | Unset):
        name (str | Unset):
        parameters (list[GetActionDefinitionsParametersItem] | Unset):
    """

    action_type: str | Unset = UNSET
    description: str | Unset = UNSET
    descriptions: list[GetActionDefinitionsDescriptionsItem] | Unset = UNSET
    help_: str | Unset = UNSET
    mission_group_id: str | Unset = UNSET
    name: str | Unset = UNSET
    parameters: list[GetActionDefinitionsParametersItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_type = self.action_type

        description = self.description

        descriptions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.descriptions, Unset):
            descriptions = []
            for descriptions_item_data in self.descriptions:
                descriptions_item = descriptions_item_data.to_dict()
                descriptions.append(descriptions_item)

        help_ = self.help_

        mission_group_id = self.mission_group_id

        name = self.name

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_type is not UNSET:
            field_dict["action_type"] = action_type
        if description is not UNSET:
            field_dict["description"] = description
        if descriptions is not UNSET:
            field_dict["descriptions"] = descriptions
        if help_ is not UNSET:
            field_dict["help"] = help_
        if mission_group_id is not UNSET:
            field_dict["mission_group_id"] = mission_group_id
        if name is not UNSET:
            field_dict["name"] = name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_action_definitions_descriptions_item import (
            GetActionDefinitionsDescriptionsItem,
        )
        from ..models.get_action_definitions_parameters_item import (
            GetActionDefinitionsParametersItem,
        )

        d = dict(src_dict)
        action_type = d.pop("action_type", UNSET)

        description = d.pop("description", UNSET)

        _descriptions = d.pop("descriptions", UNSET)
        descriptions: list[GetActionDefinitionsDescriptionsItem] | Unset = UNSET
        if _descriptions is not UNSET:
            descriptions = []
            for descriptions_item_data in _descriptions:
                descriptions_item = GetActionDefinitionsDescriptionsItem.from_dict(
                    descriptions_item_data
                )

                descriptions.append(descriptions_item)

        help_ = d.pop("help", UNSET)

        mission_group_id = d.pop("mission_group_id", UNSET)

        name = d.pop("name", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: list[GetActionDefinitionsParametersItem] | Unset = UNSET
        if _parameters is not UNSET:
            parameters = []
            for parameters_item_data in _parameters:
                parameters_item = GetActionDefinitionsParametersItem.from_dict(parameters_item_data)

                parameters.append(parameters_item)

        get_action_definitions = cls(
            action_type=action_type,
            description=description,
            descriptions=descriptions,
            help_=help_,
            mission_group_id=mission_group_id,
            name=name,
            parameters=parameters,
        )

        get_action_definitions.additional_properties = d
        return get_action_definitions

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
