from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMission")


@_attrs_define
class GetMission:
    """
    Attributes:
        actions (str | Unset): The url to the list of actions contained in this mission
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        definition (str | Unset): The url to the list of input parameters this mission accepts
        description (str | Unset): The description of the mission
        group_id (str | Unset): The id of the area this mission belongs to, or null if the mission belongs to all areas
        guid (str | Unset): The global id unique across robots that identifies this mission
        has_user_parameters (bool | Unset): Indicates if the mission has dynamic parameters
        hidden (bool | Unset): If this mission is hidden in the mission list
        is_template (bool | Unset): True if the missions is a template mission
        name (str | Unset): The name of the mission
        session_id (str | Unset): The id of the area this mission belongs to, or null if the mission belongs to all
            areas
        valid (bool | Unset): Indicates if the mission contains only existing submissions
    """

    actions: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    definition: str | Unset = UNSET
    description: str | Unset = UNSET
    group_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    has_user_parameters: bool | Unset = UNSET
    hidden: bool | Unset = UNSET
    is_template: bool | Unset = UNSET
    name: str | Unset = UNSET
    session_id: str | Unset = UNSET
    valid: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actions = self.actions

        created_by = self.created_by

        created_by_id = self.created_by_id

        definition = self.definition

        description = self.description

        group_id = self.group_id

        guid = self.guid

        has_user_parameters = self.has_user_parameters

        hidden = self.hidden

        is_template = self.is_template

        name = self.name

        session_id = self.session_id

        valid = self.valid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if definition is not UNSET:
            field_dict["definition"] = definition
        if description is not UNSET:
            field_dict["description"] = description
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if has_user_parameters is not UNSET:
            field_dict["has_user_parameters"] = has_user_parameters
        if hidden is not UNSET:
            field_dict["hidden"] = hidden
        if is_template is not UNSET:
            field_dict["is_template"] = is_template
        if name is not UNSET:
            field_dict["name"] = name
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if valid is not UNSET:
            field_dict["valid"] = valid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        actions = d.pop("actions", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        definition = d.pop("definition", UNSET)

        description = d.pop("description", UNSET)

        group_id = d.pop("group_id", UNSET)

        guid = d.pop("guid", UNSET)

        has_user_parameters = d.pop("has_user_parameters", UNSET)

        hidden = d.pop("hidden", UNSET)

        is_template = d.pop("is_template", UNSET)

        name = d.pop("name", UNSET)

        session_id = d.pop("session_id", UNSET)

        valid = d.pop("valid", UNSET)

        get_mission = cls(
            actions=actions,
            created_by=created_by,
            created_by_id=created_by_id,
            definition=definition,
            description=description,
            group_id=group_id,
            guid=guid,
            has_user_parameters=has_user_parameters,
            hidden=hidden,
            is_template=is_template,
            name=name,
            session_id=session_id,
            valid=valid,
        )

        get_mission.additional_properties = d
        return get_mission

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
