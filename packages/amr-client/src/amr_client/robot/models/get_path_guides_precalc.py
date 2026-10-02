from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPathGuidesPrecalc")


@_attrs_define
class GetPathGuidesPrecalc:
    """
    Attributes:
        active (bool | Unset): Boolean indicating if a path guide precalculation is in progress
        fail_count (int | Unset): The number of paths that was not possible to precalculate
        message (str | Unset): Status message from the precalculation module
        path_guide_guid (str | Unset): The global unique id across robots that identifies the path guide being
            precalculated
        success_count (int | Unset): The number of paths that has been successfully calculated
        total_count (int | Unset): The number of total paths to calculate
    """

    active: bool | Unset = UNSET
    fail_count: int | Unset = UNSET
    message: str | Unset = UNSET
    path_guide_guid: str | Unset = UNSET
    success_count: int | Unset = UNSET
    total_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active = self.active

        fail_count = self.fail_count

        message = self.message

        path_guide_guid = self.path_guide_guid

        success_count = self.success_count

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active is not UNSET:
            field_dict["active"] = active
        if fail_count is not UNSET:
            field_dict["fail_count"] = fail_count
        if message is not UNSET:
            field_dict["message"] = message
        if path_guide_guid is not UNSET:
            field_dict["path_guide_guid"] = path_guide_guid
        if success_count is not UNSET:
            field_dict["success_count"] = success_count
        if total_count is not UNSET:
            field_dict["total_count"] = total_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        active = d.pop("active", UNSET)

        fail_count = d.pop("fail_count", UNSET)

        message = d.pop("message", UNSET)

        path_guide_guid = d.pop("path_guide_guid", UNSET)

        success_count = d.pop("success_count", UNSET)

        total_count = d.pop("total_count", UNSET)

        get_path_guides_precalc = cls(
            active=active,
            fail_count=fail_count,
            message=message,
            path_guide_guid=path_guide_guid,
            success_count=success_count,
            total_count=total_count,
        )

        get_path_guides_precalc.additional_properties = d
        return get_path_guides_precalc

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
