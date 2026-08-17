from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.charger_type import ChargerType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entry_position_1 import EntryPosition1
    from ..models.pose_1 import Pose1


T = TypeVar("T", bound="Charger1")


@_attrs_define
class Charger1:
    """
    Attributes:
        type_ (ChargerType):
        map_id (str | Unset):
        name (str | Unset):
        map_pose (Pose1 | Unset):
        entry_position_offset_pose (Pose1 | Unset):
        entry_positions (list[EntryPosition1] | Unset):
    """

    type_: ChargerType
    map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    map_pose: Pose1 | Unset = UNSET
    entry_position_offset_pose: Pose1 | Unset = UNSET
    entry_positions: list[EntryPosition1] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        map_id = self.map_id

        name = self.name

        map_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.map_pose, Unset):
            map_pose = self.map_pose.to_dict()

        entry_position_offset_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.entry_position_offset_pose, Unset):
            entry_position_offset_pose = self.entry_position_offset_pose.to_dict()

        entry_positions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.entry_positions, Unset):
            entry_positions = []
            for entry_positions_item_data in self.entry_positions:
                entry_positions_item = entry_positions_item_data.to_dict()
                entry_positions.append(entry_positions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if map_id is not UNSET:
            field_dict["map-id"] = map_id
        if name is not UNSET:
            field_dict["name"] = name
        if map_pose is not UNSET:
            field_dict["map-pose"] = map_pose
        if entry_position_offset_pose is not UNSET:
            field_dict["entry-position-offset-pose"] = entry_position_offset_pose
        if entry_positions is not UNSET:
            field_dict["entry-positions"] = entry_positions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entry_position_1 import EntryPosition1
        from ..models.pose_1 import Pose1

        d = dict(src_dict)
        type_ = ChargerType(d.pop("type"))

        map_id = d.pop("map-id", UNSET)

        name = d.pop("name", UNSET)

        _map_pose = d.pop("map-pose", UNSET)
        map_pose: Pose1 | Unset
        if isinstance(_map_pose, Unset):
            map_pose = UNSET
        else:
            map_pose = Pose1.from_dict(_map_pose)

        _entry_position_offset_pose = d.pop("entry-position-offset-pose", UNSET)
        entry_position_offset_pose: Pose1 | Unset
        if isinstance(_entry_position_offset_pose, Unset):
            entry_position_offset_pose = UNSET
        else:
            entry_position_offset_pose = Pose1.from_dict(_entry_position_offset_pose)

        _entry_positions = d.pop("entry-positions", UNSET)
        entry_positions: list[EntryPosition1] | Unset = UNSET
        if _entry_positions is not UNSET:
            entry_positions = []
            for entry_positions_item_data in _entry_positions:
                entry_positions_item = EntryPosition1.from_dict(entry_positions_item_data)

                entry_positions.append(entry_positions_item)

        charger_1 = cls(
            type_=type_,
            map_id=map_id,
            name=name,
            map_pose=map_pose,
            entry_position_offset_pose=entry_position_offset_pose,
            entry_positions=entry_positions,
        )

        charger_1.additional_properties = d
        return charger_1

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
