from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.idle import Idle
    from ..models.not_operational import NotOperational
    from ..models.operational import Operational


T = TypeVar("T", bound="RobotState")


@_attrs_define
class RobotState:
    """
    Attributes:
        idle (Idle | Unset):
        operational (Operational | Unset):
        not_operational (NotOperational | Unset):
    """

    idle: Idle | Unset = UNSET
    operational: Operational | Unset = UNSET
    not_operational: NotOperational | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        idle: dict[str, Any] | Unset = UNSET
        if not isinstance(self.idle, Unset):
            idle = self.idle.to_dict()

        operational: dict[str, Any] | Unset = UNSET
        if not isinstance(self.operational, Unset):
            operational = self.operational.to_dict()

        not_operational: dict[str, Any] | Unset = UNSET
        if not isinstance(self.not_operational, Unset):
            not_operational = self.not_operational.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if idle is not UNSET:
            field_dict["idle"] = idle
        if operational is not UNSET:
            field_dict["operational"] = operational
        if not_operational is not UNSET:
            field_dict["not-operational"] = not_operational

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.idle import Idle
        from ..models.not_operational import NotOperational
        from ..models.operational import Operational

        d = dict(src_dict)
        _idle = d.pop("idle", UNSET)
        idle: Idle | Unset
        if isinstance(_idle, Unset):
            idle = UNSET
        else:
            idle = Idle.from_dict(_idle)

        _operational = d.pop("operational", UNSET)
        operational: Operational | Unset
        if isinstance(_operational, Unset):
            operational = UNSET
        else:
            operational = Operational.from_dict(_operational)

        _not_operational = d.pop("not-operational", UNSET)
        not_operational: NotOperational | Unset
        if isinstance(_not_operational, Unset):
            not_operational = UNSET
        else:
            not_operational = NotOperational.from_dict(_not_operational)

        robot_state = cls(
            idle=idle,
            operational=operational,
            not_operational=not_operational,
        )

        return robot_state
