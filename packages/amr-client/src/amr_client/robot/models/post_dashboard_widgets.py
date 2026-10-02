from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostDashboardWidgets")


@_attrs_define
class PostDashboardWidgets:
    """
    Attributes:
        dashboard_id (str):
        guid (str | Unset):
        settings (str | Unset):
    """

    dashboard_id: str
    guid: str | Unset = UNSET
    settings: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dashboard_id = self.dashboard_id

        guid = self.guid

        settings = self.settings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dashboard_id": dashboard_id,
            }
        )
        if guid is not UNSET:
            field_dict["guid"] = guid
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dashboard_id = d.pop("dashboard_id")

        guid = d.pop("guid", UNSET)

        settings = d.pop("settings", UNSET)

        post_dashboard_widgets = cls(
            dashboard_id=dashboard_id,
            guid=guid,
            settings=settings,
        )

        post_dashboard_widgets.additional_properties = d
        return post_dashboard_widgets

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
