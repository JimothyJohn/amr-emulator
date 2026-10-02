from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.brake_state import BrakeState
from ..models.gripper_state import GripperState
from ..models.height_state import HeightState
from ..types import UNSET, Unset

T = TypeVar("T", bound="HookData")


@_attrs_define
class HookData:
    """
    Attributes:
        angle (float):
        height (float):
        brake_state (BrakeState):
        gripper_state (GripperState):
        height_state (HeightState):
        trolley_attached (bool):
        trolley_id (None | str | Unset):
    """

    angle: float
    height: float
    brake_state: BrakeState
    gripper_state: GripperState
    height_state: HeightState
    trolley_attached: bool
    trolley_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        angle = self.angle

        height = self.height

        brake_state = self.brake_state.value

        gripper_state = self.gripper_state.value

        height_state = self.height_state.value

        trolley_attached = self.trolley_attached

        trolley_id: None | str | Unset
        if isinstance(self.trolley_id, Unset):
            trolley_id = UNSET
        else:
            trolley_id = self.trolley_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "angle": angle,
                "height": height,
                "brake-state": brake_state,
                "gripper-state": gripper_state,
                "height-state": height_state,
                "trolley-attached": trolley_attached,
            }
        )
        if trolley_id is not UNSET:
            field_dict["trolley-id"] = trolley_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        angle = d.pop("angle")

        height = d.pop("height")

        brake_state = BrakeState(d.pop("brake-state"))

        gripper_state = GripperState(d.pop("gripper-state"))

        height_state = HeightState(d.pop("height-state"))

        trolley_attached = d.pop("trolley-attached")

        def _parse_trolley_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        trolley_id = _parse_trolley_id(d.pop("trolley-id", UNSET))

        hook_data = cls(
            angle=angle,
            height=height,
            brake_state=brake_state,
            gripper_state=gripper_state,
            height_state=height_state,
            trolley_attached=trolley_attached,
            trolley_id=trolley_id,
        )

        return hook_data
