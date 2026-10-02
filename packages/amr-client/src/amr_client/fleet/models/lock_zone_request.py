from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="LockZoneRequest")


@_attrs_define
class LockZoneRequest:
    """
    Attributes:
        zone_id (UUID):
        is_locked (bool):
    """

    zone_id: UUID
    is_locked: bool

    def to_dict(self) -> dict[str, Any]:
        zone_id = str(self.zone_id)

        is_locked = self.is_locked

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "zone-id": zone_id,
                "is-locked": is_locked,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        zone_id = UUID(d.pop("zone-id"))

        is_locked = d.pop("is-locked")

        lock_zone_request = cls(
            zone_id=zone_id,
            is_locked=is_locked,
        )

        return lock_zone_request
