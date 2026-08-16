from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pose_1 import Pose1


T = TypeVar("T", bound="PositionProperties")


@_attrs_define
class PositionProperties:
    """
    Attributes:
        type_ (str):
        map_id (str | Unset):
        name (str | Unset):
        map_pose (Pose1 | Unset):
    """

    type_: str
    map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    map_pose: Pose1 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        map_id = self.map_id

        name = self.name

        map_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.map_pose, Unset):
            map_pose = self.map_pose.to_dict()

        field_dict: dict[str, Any] = {}

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pose_1 import Pose1

        d = dict(src_dict)
        type_ = d.pop("type")

        map_id = d.pop("map-id", UNSET)

        name = d.pop("name", UNSET)

        _map_pose = d.pop("map-pose", UNSET)
        map_pose: Pose1 | Unset
        if isinstance(_map_pose, Unset):
            map_pose = UNSET
        else:
            map_pose = Pose1.from_dict(_map_pose)

        position_properties = cls(
            type_=type_,
            map_id=map_id,
            name=name,
            map_pose=map_pose,
        )

        return position_properties
