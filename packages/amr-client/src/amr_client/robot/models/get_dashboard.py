from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDashboard")


@_attrs_define
class GetDashboard:
    """
    Attributes:
        created_by (str | Unset): The url to the user that created the dashboard
        created_by_id (str | Unset): The global id of the user who created this entry
        fleet_dashboard (bool | Unset):
        guid (str | Unset): The global id unique across robots that identifies this dashboard
        name (str | Unset): The name of this dashboard
        widgets (str | Unset): The url to the possible widgets. if the dashboard does not have any widgets then this
            field is empty
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    fleet_dashboard: bool | Unset = UNSET
    guid: str | Unset = UNSET
    name: str | Unset = UNSET
    widgets: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        fleet_dashboard = self.fleet_dashboard

        guid = self.guid

        name = self.name

        widgets = self.widgets

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if fleet_dashboard is not UNSET:
            field_dict["fleet_dashboard"] = fleet_dashboard
        if guid is not UNSET:
            field_dict["guid"] = guid
        if name is not UNSET:
            field_dict["name"] = name
        if widgets is not UNSET:
            field_dict["widgets"] = widgets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        fleet_dashboard = d.pop("fleet_dashboard", UNSET)

        guid = d.pop("guid", UNSET)

        name = d.pop("name", UNSET)

        widgets = d.pop("widgets", UNSET)

        get_dashboard = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            fleet_dashboard=fleet_dashboard,
            guid=guid,
            name=name,
            widgets=widgets,
        )

        get_dashboard.additional_properties = d
        return get_dashboard

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
