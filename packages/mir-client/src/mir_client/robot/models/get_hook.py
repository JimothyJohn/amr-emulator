from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_hook_brake import GetHookBrake
    from ..models.get_hook_gripper import GetHookGripper
    from ..models.get_hook_height import GetHookHeight


T = TypeVar("T", bound="GetHook")


@_attrs_define
class GetHook:
    """
    Attributes:
        angle (float | Unset): The angle of the hook arm
        available (bool | Unset): Whether the hook data is available or not
        brake (GetHookBrake | Unset):
        gripper (GetHookGripper | Unset):
        height (GetHookHeight | Unset):
    """

    angle: float | Unset = UNSET
    available: bool | Unset = UNSET
    brake: GetHookBrake | Unset = UNSET
    gripper: GetHookGripper | Unset = UNSET
    height: GetHookHeight | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        angle = self.angle

        available = self.available

        brake: dict[str, Any] | Unset = UNSET
        if not isinstance(self.brake, Unset):
            brake = self.brake.to_dict()

        gripper: dict[str, Any] | Unset = UNSET
        if not isinstance(self.gripper, Unset):
            gripper = self.gripper.to_dict()

        height: dict[str, Any] | Unset = UNSET
        if not isinstance(self.height, Unset):
            height = self.height.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if angle is not UNSET:
            field_dict["angle"] = angle
        if available is not UNSET:
            field_dict["available"] = available
        if brake is not UNSET:
            field_dict["brake"] = brake
        if gripper is not UNSET:
            field_dict["gripper"] = gripper
        if height is not UNSET:
            field_dict["height"] = height

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_hook_brake import GetHookBrake
        from ..models.get_hook_gripper import GetHookGripper
        from ..models.get_hook_height import GetHookHeight

        d = dict(src_dict)
        angle = d.pop("angle", UNSET)

        available = d.pop("available", UNSET)

        _brake = d.pop("brake", UNSET)
        brake: GetHookBrake | Unset
        if isinstance(_brake, Unset):
            brake = UNSET
        else:
            brake = GetHookBrake.from_dict(_brake)

        _gripper = d.pop("gripper", UNSET)
        gripper: GetHookGripper | Unset
        if isinstance(_gripper, Unset):
            gripper = UNSET
        else:
            gripper = GetHookGripper.from_dict(_gripper)

        _height = d.pop("height", UNSET)
        height: GetHookHeight | Unset
        if isinstance(_height, Unset):
            height = UNSET
        else:
            height = GetHookHeight.from_dict(_height)

        get_hook = cls(
            angle=angle,
            available=available,
            brake=brake,
            gripper=gripper,
            height=height,
        )

        get_hook.additional_properties = d
        return get_hook

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
