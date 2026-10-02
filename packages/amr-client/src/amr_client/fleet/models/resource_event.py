from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResourceEvent")


@_attrs_define
class ResourceEvent:
    """
    Attributes:
        resource_type (str | Unset):
        resource_id (str | Unset):
        resource_name (str | Unset):
        assigned_robot_ids (list[str] | Unset):
        enqueued_robot_ids (list[str] | Unset):
    """

    resource_type: str | Unset = UNSET
    resource_id: str | Unset = UNSET
    resource_name: str | Unset = UNSET
    assigned_robot_ids: list[str] | Unset = UNSET
    enqueued_robot_ids: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        resource_type = self.resource_type

        resource_id = self.resource_id

        resource_name = self.resource_name

        assigned_robot_ids: list[str] | Unset = UNSET
        if not isinstance(self.assigned_robot_ids, Unset):
            assigned_robot_ids = self.assigned_robot_ids

        enqueued_robot_ids: list[str] | Unset = UNSET
        if not isinstance(self.enqueued_robot_ids, Unset):
            enqueued_robot_ids = self.enqueued_robot_ids

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if resource_type is not UNSET:
            field_dict["resource-type"] = resource_type
        if resource_id is not UNSET:
            field_dict["resource-id"] = resource_id
        if resource_name is not UNSET:
            field_dict["resource-name"] = resource_name
        if assigned_robot_ids is not UNSET:
            field_dict["assigned-robot-ids"] = assigned_robot_ids
        if enqueued_robot_ids is not UNSET:
            field_dict["enqueued-robot-ids"] = enqueued_robot_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resource_type = d.pop("resource-type", UNSET)

        resource_id = d.pop("resource-id", UNSET)

        resource_name = d.pop("resource-name", UNSET)

        assigned_robot_ids = cast(list[str], d.pop("assigned-robot-ids", UNSET))

        enqueued_robot_ids = cast(list[str], d.pop("enqueued-robot-ids", UNSET))

        resource_event = cls(
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            assigned_robot_ids=assigned_robot_ids,
            enqueued_robot_ids=enqueued_robot_ids,
        )

        return resource_event
