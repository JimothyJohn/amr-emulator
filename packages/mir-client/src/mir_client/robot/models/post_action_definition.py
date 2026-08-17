from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_action_definition_parameters_item import PostActionDefinitionParametersItem


T = TypeVar("T", bound="PostActionDefinition")


@_attrs_define
class PostActionDefinition:
    """
    Attributes:
        parameters (list[PostActionDefinitionParametersItem]):
    """

    parameters: list[PostActionDefinitionParametersItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        parameters = []
        for parameters_item_data in self.parameters:
            parameters_item = parameters_item_data.to_dict()
            parameters.append(parameters_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "parameters": parameters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_action_definition_parameters_item import (
            PostActionDefinitionParametersItem,
        )

        d = dict(src_dict)
        parameters = []
        _parameters = d.pop("parameters")
        for parameters_item_data in _parameters:
            parameters_item = PostActionDefinitionParametersItem.from_dict(parameters_item_data)

            parameters.append(parameters_item)

        post_action_definition = cls(
            parameters=parameters,
        )

        post_action_definition.additional_properties = d
        return post_action_definition

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
