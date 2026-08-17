from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SystemVersionResponse")


@_attrs_define
class SystemVersionResponse:
    """
    Attributes:
        version (str | Unset):
        fleet_name (str | Unset):
    """

    version: str | Unset = UNSET
    fleet_name: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        fleet_name = self.fleet_name

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if version is not UNSET:
            field_dict["version"] = version
        if fleet_name is not UNSET:
            field_dict["fleet-name"] = fleet_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version = d.pop("version", UNSET)

        fleet_name = d.pop("fleet-name", UNSET)

        system_version_response = cls(
            version=version,
            fleet_name=fleet_name,
        )

        return system_version_response
