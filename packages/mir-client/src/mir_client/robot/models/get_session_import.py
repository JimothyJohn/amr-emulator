from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSessionImport")


@_attrs_define
class GetSessionImport:
    """
    Attributes:
        error_message (str | Unset): A description of this action
        sessions_imported (int | Unset): The type of area action
        sessions_total (int | Unset): A name associated with this area action
        status (int | Unset): A nice name associated with this area action
    """

    error_message: str | Unset = UNSET
    sessions_imported: int | Unset = UNSET
    sessions_total: int | Unset = UNSET
    status: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error_message = self.error_message

        sessions_imported = self.sessions_imported

        sessions_total = self.sessions_total

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if sessions_imported is not UNSET:
            field_dict["sessions_imported"] = sessions_imported
        if sessions_total is not UNSET:
            field_dict["sessions_total"] = sessions_total
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error_message = d.pop("error_message", UNSET)

        sessions_imported = d.pop("sessions_imported", UNSET)

        sessions_total = d.pop("sessions_total", UNSET)

        status = d.pop("status", UNSET)

        get_session_import = cls(
            error_message=error_message,
            sessions_imported=sessions_imported,
            sessions_total=sessions_total,
            status=status,
        )

        get_session_import.additional_properties = d
        return get_session_import

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
