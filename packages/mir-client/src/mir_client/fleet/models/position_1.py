from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.base_position_1 import BasePosition1
    from ..models.charger_1 import Charger1
    from ..models.marker_1 import Marker1
    from ..models.utility_position_1 import UtilityPosition1


T = TypeVar("T", bound="Position1")


@_attrs_define
class Position1:
    """
    Attributes:
        base_position (BasePosition1 | Unset):
        marker (Marker1 | Unset):
        charger (Charger1 | Unset):
        utility_position (UtilityPosition1 | Unset):
    """

    base_position: BasePosition1 | Unset = UNSET
    marker: Marker1 | Unset = UNSET
    charger: Charger1 | Unset = UNSET
    utility_position: UtilityPosition1 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        base_position: dict[str, Any] | Unset = UNSET
        if not isinstance(self.base_position, Unset):
            base_position = self.base_position.to_dict()

        marker: dict[str, Any] | Unset = UNSET
        if not isinstance(self.marker, Unset):
            marker = self.marker.to_dict()

        charger: dict[str, Any] | Unset = UNSET
        if not isinstance(self.charger, Unset):
            charger = self.charger.to_dict()

        utility_position: dict[str, Any] | Unset = UNSET
        if not isinstance(self.utility_position, Unset):
            utility_position = self.utility_position.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if base_position is not UNSET:
            field_dict["base-position"] = base_position
        if marker is not UNSET:
            field_dict["marker"] = marker
        if charger is not UNSET:
            field_dict["charger"] = charger
        if utility_position is not UNSET:
            field_dict["utility-position"] = utility_position

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.base_position_1 import BasePosition1
        from ..models.charger_1 import Charger1
        from ..models.marker_1 import Marker1
        from ..models.utility_position_1 import UtilityPosition1

        d = dict(src_dict)
        _base_position = d.pop("base-position", UNSET)
        base_position: BasePosition1 | Unset
        if isinstance(_base_position, Unset):
            base_position = UNSET
        else:
            base_position = BasePosition1.from_dict(_base_position)

        _marker = d.pop("marker", UNSET)
        marker: Marker1 | Unset
        if isinstance(_marker, Unset):
            marker = UNSET
        else:
            marker = Marker1.from_dict(_marker)

        _charger = d.pop("charger", UNSET)
        charger: Charger1 | Unset
        if isinstance(_charger, Unset):
            charger = UNSET
        else:
            charger = Charger1.from_dict(_charger)

        _utility_position = d.pop("utility-position", UNSET)
        utility_position: UtilityPosition1 | Unset
        if isinstance(_utility_position, Unset):
            utility_position = UNSET
        else:
            utility_position = UtilityPosition1.from_dict(_utility_position)

        position_1 = cls(
            base_position=base_position,
            marker=marker,
            charger=charger,
            utility_position=utility_position,
        )

        return position_1
