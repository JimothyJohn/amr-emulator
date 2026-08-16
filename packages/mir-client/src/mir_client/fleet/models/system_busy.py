from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.shutting_down import ShuttingDown
    from ..models.starting import Starting


T = TypeVar("T", bound="SystemBusy")


@_attrs_define
class SystemBusy:
    """
    Attributes:
        starting (Starting | Unset):
        shutting_down (ShuttingDown | Unset):
    """

    starting: Starting | Unset = UNSET
    shutting_down: ShuttingDown | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        starting: dict[str, Any] | Unset = UNSET
        if not isinstance(self.starting, Unset):
            starting = self.starting.to_dict()

        shutting_down: dict[str, Any] | Unset = UNSET
        if not isinstance(self.shutting_down, Unset):
            shutting_down = self.shutting_down.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if starting is not UNSET:
            field_dict["starting"] = starting
        if shutting_down is not UNSET:
            field_dict["shutting-down"] = shutting_down

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.shutting_down import ShuttingDown
        from ..models.starting import Starting

        d = dict(src_dict)
        _starting = d.pop("starting", UNSET)
        starting: Starting | Unset
        if isinstance(_starting, Unset):
            starting = UNSET
        else:
            starting = Starting.from_dict(_starting)

        _shutting_down = d.pop("shutting-down", UNSET)
        shutting_down: ShuttingDown | Unset
        if isinstance(_shutting_down, Unset):
            shutting_down = UNSET
        else:
            shutting_down = ShuttingDown.from_dict(_shutting_down)

        system_busy = cls(
            starting=starting,
            shutting_down=shutting_down,
        )

        return system_busy
