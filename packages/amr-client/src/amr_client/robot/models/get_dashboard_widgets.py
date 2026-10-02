from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDashboardWidgets")


@_attrs_define
class GetDashboardWidgets:
    """
    Attributes:
        dashboard_id (str | Unset): The guid of the dashboard this widget belongs to
        guid (str | Unset): The global id unique across robots that identifies this widget
        url (str | Unset): The URL of the resource
    """

    dashboard_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dashboard_id = self.dashboard_id

        guid = self.guid

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dashboard_id is not UNSET:
            field_dict["dashboard_id"] = dashboard_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dashboard_id = d.pop("dashboard_id", UNSET)

        guid = d.pop("guid", UNSET)

        url = d.pop("url", UNSET)

        get_dashboard_widgets = cls(
            dashboard_id=dashboard_id,
            guid=guid,
            url=url,
        )

        get_dashboard_widgets.additional_properties = d
        return get_dashboard_widgets

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
