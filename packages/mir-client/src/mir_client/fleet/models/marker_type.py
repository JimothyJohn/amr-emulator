from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.docking_type import DockingType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pose_1 import Pose1


T = TypeVar("T", bound="MarkerType")


@_attrs_define
class MarkerType:
    """
    Attributes:
        name (str):
        docking_type (DockingType):
        offset (Pose1):
        length (float):
        distance (float):
        shelf_leg_asymmetry (float | None | Unset):
    """

    name: str
    docking_type: DockingType
    offset: Pose1
    length: float
    distance: float
    shelf_leg_asymmetry: float | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        docking_type = self.docking_type.value

        offset = self.offset.to_dict()

        length = self.length

        distance = self.distance

        shelf_leg_asymmetry: float | None | Unset
        if isinstance(self.shelf_leg_asymmetry, Unset):
            shelf_leg_asymmetry = UNSET
        else:
            shelf_leg_asymmetry = self.shelf_leg_asymmetry

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "docking-type": docking_type,
                "offset": offset,
                "length": length,
                "distance": distance,
            }
        )
        if shelf_leg_asymmetry is not UNSET:
            field_dict["shelf-leg-asymmetry"] = shelf_leg_asymmetry

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pose_1 import Pose1

        d = dict(src_dict)
        name = d.pop("name")

        docking_type = DockingType(d.pop("docking-type"))

        offset = Pose1.from_dict(d.pop("offset"))

        length = d.pop("length")

        distance = d.pop("distance")

        def _parse_shelf_leg_asymmetry(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        shelf_leg_asymmetry = _parse_shelf_leg_asymmetry(d.pop("shelf-leg-asymmetry", UNSET))

        marker_type = cls(
            name=name,
            docking_type=docking_type,
            offset=offset,
            length=length,
            distance=distance,
            shelf_leg_asymmetry=shelf_leg_asymmetry,
        )

        return marker_type
