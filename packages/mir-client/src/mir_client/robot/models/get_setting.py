from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_setting_constraints import GetSettingConstraints


T = TypeVar("T", bound="GetSetting")


@_attrs_define
class GetSetting:
    """
    Attributes:
        children_ids (str | Unset):
        constraints (GetSettingConstraints | Unset):
        default (str | Unset):
        description (str | Unset):
        disclaimer_text (str | Unset):
        editable (str | Unset):
        fieldtype (str | Unset):
        full_name (str | Unset):
        id (int | Unset):
        name (str | Unset):
        parent_id (str | Unset):
        parent_name (str | Unset):
        parent_value (str | Unset):
        settings_group (str | Unset):
        settings_group_id (int | Unset):
        type_ (str | Unset):
        value (str | Unset):
    """

    children_ids: str | Unset = UNSET
    constraints: GetSettingConstraints | Unset = UNSET
    default: str | Unset = UNSET
    description: str | Unset = UNSET
    disclaimer_text: str | Unset = UNSET
    editable: str | Unset = UNSET
    fieldtype: str | Unset = UNSET
    full_name: str | Unset = UNSET
    id: int | Unset = UNSET
    name: str | Unset = UNSET
    parent_id: str | Unset = UNSET
    parent_name: str | Unset = UNSET
    parent_value: str | Unset = UNSET
    settings_group: str | Unset = UNSET
    settings_group_id: int | Unset = UNSET
    type_: str | Unset = UNSET
    value: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        children_ids = self.children_ids

        constraints: dict[str, Any] | Unset = UNSET
        if not isinstance(self.constraints, Unset):
            constraints = self.constraints.to_dict()

        default = self.default

        description = self.description

        disclaimer_text = self.disclaimer_text

        editable = self.editable

        fieldtype = self.fieldtype

        full_name = self.full_name

        id = self.id

        name = self.name

        parent_id = self.parent_id

        parent_name = self.parent_name

        parent_value = self.parent_value

        settings_group = self.settings_group

        settings_group_id = self.settings_group_id

        type_ = self.type_

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if children_ids is not UNSET:
            field_dict["children_ids"] = children_ids
        if constraints is not UNSET:
            field_dict["constraints"] = constraints
        if default is not UNSET:
            field_dict["default"] = default
        if description is not UNSET:
            field_dict["description"] = description
        if disclaimer_text is not UNSET:
            field_dict["disclaimer_text"] = disclaimer_text
        if editable is not UNSET:
            field_dict["editable"] = editable
        if fieldtype is not UNSET:
            field_dict["fieldtype"] = fieldtype
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if parent_name is not UNSET:
            field_dict["parent_name"] = parent_name
        if parent_value is not UNSET:
            field_dict["parent_value"] = parent_value
        if settings_group is not UNSET:
            field_dict["settings_group"] = settings_group
        if settings_group_id is not UNSET:
            field_dict["settings_group_id"] = settings_group_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_setting_constraints import GetSettingConstraints

        d = dict(src_dict)
        children_ids = d.pop("children_ids", UNSET)

        _constraints = d.pop("constraints", UNSET)
        constraints: GetSettingConstraints | Unset
        if isinstance(_constraints, Unset):
            constraints = UNSET
        else:
            constraints = GetSettingConstraints.from_dict(_constraints)

        default = d.pop("default", UNSET)

        description = d.pop("description", UNSET)

        disclaimer_text = d.pop("disclaimer_text", UNSET)

        editable = d.pop("editable", UNSET)

        fieldtype = d.pop("fieldtype", UNSET)

        full_name = d.pop("full_name", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        parent_id = d.pop("parent_id", UNSET)

        parent_name = d.pop("parent_name", UNSET)

        parent_value = d.pop("parent_value", UNSET)

        settings_group = d.pop("settings_group", UNSET)

        settings_group_id = d.pop("settings_group_id", UNSET)

        type_ = d.pop("type", UNSET)

        value = d.pop("value", UNSET)

        get_setting = cls(
            children_ids=children_ids,
            constraints=constraints,
            default=default,
            description=description,
            disclaimer_text=disclaimer_text,
            editable=editable,
            fieldtype=fieldtype,
            full_name=full_name,
            id=id,
            name=name,
            parent_id=parent_id,
            parent_name=parent_name,
            parent_value=parent_value,
            settings_group=settings_group,
            settings_group_id=settings_group_id,
            type_=type_,
            value=value,
        )

        get_setting.additional_properties = d
        return get_setting

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
