from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDashboardWidget")


@_attrs_define
class GetDashboardWidget:
    """
    Attributes:
        created_by_id (str | Unset): User guid of the user of the dashboard which the widget belongs to
        dashboard (str | Unset): The url to the dashboard where this widget belongs.
        dashboard_id (str | Unset): The guid of the dashboard this widget belongs to
        guid (str | Unset): The global id unique across robots that identifies this widget
        settings (str | Unset): Widgets configuration encoded base 64 in json
    """

    created_by_id: str | Unset = UNSET
    dashboard: str | Unset = UNSET
    dashboard_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    settings: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by_id = self.created_by_id

        dashboard = self.dashboard

        dashboard_id = self.dashboard_id

        guid = self.guid

        settings = self.settings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if dashboard is not UNSET:
            field_dict["dashboard"] = dashboard
        if dashboard_id is not UNSET:
            field_dict["dashboard_id"] = dashboard_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by_id = d.pop("created_by_id", UNSET)

        dashboard = d.pop("dashboard", UNSET)

        dashboard_id = d.pop("dashboard_id", UNSET)

        guid = d.pop("guid", UNSET)

        settings = d.pop("settings", UNSET)

        get_dashboard_widget = cls(
            created_by_id=created_by_id,
            dashboard=dashboard,
            dashboard_id=dashboard_id,
            guid=guid,
            settings=settings,
        )

        get_dashboard_widget.additional_properties = d
        return get_dashboard_widget

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
