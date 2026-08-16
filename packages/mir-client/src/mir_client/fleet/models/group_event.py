from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_1 import Group1
    from ..models.mission_group import MissionGroup


T = TypeVar("T", bound="GroupEvent")


@_attrs_define
class GroupEvent:
    """
    Attributes:
        entity_id (str):
        entity_type (str):
        action_type (None | str | Unset):
        status_change_timestamp (datetime.datetime | Unset):
        group (Group1 | Unset):
        mission_group (MissionGroup | Unset):
    """

    entity_id: str
    entity_type: str
    action_type: None | str | Unset = UNSET
    status_change_timestamp: datetime.datetime | Unset = UNSET
    group: Group1 | Unset = UNSET
    mission_group: MissionGroup | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        entity_id = self.entity_id

        entity_type = self.entity_type

        action_type: None | str | Unset
        if isinstance(self.action_type, Unset):
            action_type = UNSET
        else:
            action_type = self.action_type

        status_change_timestamp: str | Unset = UNSET
        if not isinstance(self.status_change_timestamp, Unset):
            status_change_timestamp = self.status_change_timestamp.isoformat()

        group: dict[str, Any] | Unset = UNSET
        if not isinstance(self.group, Unset):
            group = self.group.to_dict()

        mission_group: dict[str, Any] | Unset = UNSET
        if not isinstance(self.mission_group, Unset):
            mission_group = self.mission_group.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "entity-id": entity_id,
                "entity-type": entity_type,
            }
        )
        if action_type is not UNSET:
            field_dict["action-type"] = action_type
        if status_change_timestamp is not UNSET:
            field_dict["status-change-timestamp"] = status_change_timestamp
        if group is not UNSET:
            field_dict["group"] = group
        if mission_group is not UNSET:
            field_dict["mission-group"] = mission_group

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_1 import Group1
        from ..models.mission_group import MissionGroup

        d = dict(src_dict)
        entity_id = d.pop("entity-id")

        entity_type = d.pop("entity-type")

        def _parse_action_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action_type = _parse_action_type(d.pop("action-type", UNSET))

        _status_change_timestamp = d.pop("status-change-timestamp", UNSET)
        status_change_timestamp: datetime.datetime | Unset
        if isinstance(_status_change_timestamp, Unset):
            status_change_timestamp = UNSET
        else:
            status_change_timestamp = datetime.datetime.fromisoformat(_status_change_timestamp)

        _group = d.pop("group", UNSET)
        group: Group1 | Unset
        if isinstance(_group, Unset):
            group = UNSET
        else:
            group = Group1.from_dict(_group)

        _mission_group = d.pop("mission-group", UNSET)
        mission_group: MissionGroup | Unset
        if isinstance(_mission_group, Unset):
            mission_group = UNSET
        else:
            mission_group = MissionGroup.from_dict(_mission_group)

        group_event = cls(
            entity_id=entity_id,
            entity_type=entity_type,
            action_type=action_type,
            status_change_timestamp=status_change_timestamp,
            group=group,
            mission_group=mission_group,
        )

        return group_event
