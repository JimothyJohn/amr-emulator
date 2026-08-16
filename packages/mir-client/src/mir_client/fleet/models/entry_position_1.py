from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.entry_position_type import EntryPositionType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pose_1 import Pose1


T = TypeVar("T", bound="EntryPosition1")


@_attrs_define
class EntryPosition1:
    """
    Attributes:
        entry_position_type (EntryPositionType):
        offset_pose (Pose1 | Unset):
    """

    entry_position_type: EntryPositionType
    offset_pose: Pose1 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        entry_position_type = self.entry_position_type.value

        offset_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.offset_pose, Unset):
            offset_pose = self.offset_pose.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "entry-position-type": entry_position_type,
            }
        )
        if offset_pose is not UNSET:
            field_dict["offset-pose"] = offset_pose

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pose_1 import Pose1

        d = dict(src_dict)
        entry_position_type = EntryPositionType(d.pop("entry-position-type"))

        _offset_pose = d.pop("offset-pose", UNSET)
        offset_pose: Pose1 | Unset
        if isinstance(_offset_pose, Unset):
            offset_pose = UNSET
        else:
            offset_pose = Pose1.from_dict(_offset_pose)

        entry_position_1 = cls(
            entry_position_type=entry_position_type,
            offset_pose=offset_pose,
        )

        return entry_position_1
