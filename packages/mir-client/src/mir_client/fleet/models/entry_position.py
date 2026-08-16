from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.entry_position_type import EntryPositionType

if TYPE_CHECKING:
    from ..models.pose import Pose


T = TypeVar("T", bound="EntryPosition")


@_attrs_define
class EntryPosition:
    """
    Attributes:
        entry_position_type (EntryPositionType):
        offset_pose (Pose):
    """

    entry_position_type: EntryPositionType
    offset_pose: Pose

    def to_dict(self) -> dict[str, Any]:
        entry_position_type = self.entry_position_type.value

        offset_pose = self.offset_pose.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "entry-position-type": entry_position_type,
                "offset-pose": offset_pose,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pose import Pose

        d = dict(src_dict)
        entry_position_type = EntryPositionType(d.pop("entry-position-type"))

        offset_pose = Pose.from_dict(d.pop("offset-pose"))

        entry_position = cls(
            entry_position_type=entry_position_type,
            offset_pose=offset_pose,
        )

        return entry_position
