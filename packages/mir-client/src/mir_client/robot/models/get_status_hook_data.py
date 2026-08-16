from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_status_hook_data_angle import GetStatusHookDataAngle


T = TypeVar("T", bound="GetStatusHookData")


@_attrs_define
class GetStatusHookData:
    """
    Attributes:
        angle (GetStatusHookDataAngle | Unset):
        height (float | Unset): Height of the hook measured from the ground in mm.
        length (float | Unset): Length of the hook in meters.
    """

    angle: GetStatusHookDataAngle | Unset = UNSET
    height: float | Unset = UNSET
    length: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        angle: dict[str, Any] | Unset = UNSET
        if not isinstance(self.angle, Unset):
            angle = self.angle.to_dict()

        height = self.height

        length = self.length

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if angle is not UNSET:
            field_dict["angle"] = angle
        if height is not UNSET:
            field_dict["height"] = height
        if length is not UNSET:
            field_dict["length"] = length

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_status_hook_data_angle import GetStatusHookDataAngle

        d = dict(src_dict)
        _angle = d.pop("angle", UNSET)
        angle: GetStatusHookDataAngle | Unset
        if isinstance(_angle, Unset):
            angle = UNSET
        else:
            angle = GetStatusHookDataAngle.from_dict(_angle)

        height = d.pop("height", UNSET)

        length = d.pop("length", UNSET)

        get_status_hook_data = cls(
            angle=angle,
            height=height,
            length=length,
        )

        get_status_hook_data.additional_properties = d
        return get_status_hook_data

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
