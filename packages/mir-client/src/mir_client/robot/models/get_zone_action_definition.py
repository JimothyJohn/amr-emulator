from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetZoneActionDefinition")


@_attrs_define
class GetZoneActionDefinition:
    """
    Attributes:
        action_type (str | Unset): A name associated with this area action
        action_type_id (int | Unset): The type of area action
        help_ (str | Unset): A description of this action
        limit (int | Unset): The amount of actions of this type we can add.
        name (str | Unset): A nice name associated with this area action
        parameters (str | Unset):
    """

    action_type: str | Unset = UNSET
    action_type_id: int | Unset = UNSET
    help_: str | Unset = UNSET
    limit: int | Unset = UNSET
    name: str | Unset = UNSET
    parameters: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_type = self.action_type

        action_type_id = self.action_type_id

        help_ = self.help_

        limit = self.limit

        name = self.name

        parameters = self.parameters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_type is not UNSET:
            field_dict["action_type"] = action_type
        if action_type_id is not UNSET:
            field_dict["action_type_id"] = action_type_id
        if help_ is not UNSET:
            field_dict["help"] = help_
        if limit is not UNSET:
            field_dict["limit"] = limit
        if name is not UNSET:
            field_dict["name"] = name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action_type = d.pop("action_type", UNSET)

        action_type_id = d.pop("action_type_id", UNSET)

        help_ = d.pop("help", UNSET)

        limit = d.pop("limit", UNSET)

        name = d.pop("name", UNSET)

        parameters = d.pop("parameters", UNSET)

        get_zone_action_definition = cls(
            action_type=action_type,
            action_type_id=action_type_id,
            help_=help_,
            limit=limit,
            name=name,
            parameters=parameters,
        )

        get_zone_action_definition.additional_properties = d
        return get_zone_action_definition

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
