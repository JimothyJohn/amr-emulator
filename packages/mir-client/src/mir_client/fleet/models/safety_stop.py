from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.brake_release import BrakeRelease
    from ..models.e_stop import EStop
    from ..models.p_stop import PStop
    from ..models.restart_required import RestartRequired


T = TypeVar("T", bound="SafetyStop")


@_attrs_define
class SafetyStop:
    """
    Attributes:
        p_stop (PStop | Unset):
        e_stop (EStop | Unset):
        brake_release (BrakeRelease | Unset):
        restart_required (RestartRequired | Unset):
    """

    p_stop: PStop | Unset = UNSET
    e_stop: EStop | Unset = UNSET
    brake_release: BrakeRelease | Unset = UNSET
    restart_required: RestartRequired | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        p_stop: dict[str, Any] | Unset = UNSET
        if not isinstance(self.p_stop, Unset):
            p_stop = self.p_stop.to_dict()

        e_stop: dict[str, Any] | Unset = UNSET
        if not isinstance(self.e_stop, Unset):
            e_stop = self.e_stop.to_dict()

        brake_release: dict[str, Any] | Unset = UNSET
        if not isinstance(self.brake_release, Unset):
            brake_release = self.brake_release.to_dict()

        restart_required: dict[str, Any] | Unset = UNSET
        if not isinstance(self.restart_required, Unset):
            restart_required = self.restart_required.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if p_stop is not UNSET:
            field_dict["p-stop"] = p_stop
        if e_stop is not UNSET:
            field_dict["e-stop"] = e_stop
        if brake_release is not UNSET:
            field_dict["brake-release"] = brake_release
        if restart_required is not UNSET:
            field_dict["restart-required"] = restart_required

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.brake_release import BrakeRelease
        from ..models.e_stop import EStop
        from ..models.p_stop import PStop
        from ..models.restart_required import RestartRequired

        d = dict(src_dict)
        _p_stop = d.pop("p-stop", UNSET)
        p_stop: PStop | Unset
        if isinstance(_p_stop, Unset):
            p_stop = UNSET
        else:
            p_stop = PStop.from_dict(_p_stop)

        _e_stop = d.pop("e-stop", UNSET)
        e_stop: EStop | Unset
        if isinstance(_e_stop, Unset):
            e_stop = UNSET
        else:
            e_stop = EStop.from_dict(_e_stop)

        _brake_release = d.pop("brake-release", UNSET)
        brake_release: BrakeRelease | Unset
        if isinstance(_brake_release, Unset):
            brake_release = UNSET
        else:
            brake_release = BrakeRelease.from_dict(_brake_release)

        _restart_required = d.pop("restart-required", UNSET)
        restart_required: RestartRequired | Unset
        if isinstance(_restart_required, Unset):
            restart_required = UNSET
        else:
            restart_required = RestartRequired.from_dict(_restart_required)

        safety_stop = cls(
            p_stop=p_stop,
            e_stop=e_stop,
            brake_release=brake_release,
            restart_required=restart_required,
        )

        return safety_stop
