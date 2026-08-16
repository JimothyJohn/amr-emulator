from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.robot_end_state import RobotEndState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.footprint import Footprint
    from ..models.robot_error import RobotError
    from ..models.robot_identity import RobotIdentity
    from ..models.robot_runtime import RobotRuntime
    from ..models.robot_state import RobotState


T = TypeVar("T", bound="RobotResponse")


@_attrs_define
class RobotResponse:
    """
    Attributes:
        robot_identity (RobotIdentity):
        runtime_data (RobotRuntime | Unset):
        robot_state (RobotState | Unset):
        robot_end_state (RobotEndState | Unset):
        errors (list[RobotError] | Unset):
        footprint (Footprint | Unset):
    """

    robot_identity: RobotIdentity
    runtime_data: RobotRuntime | Unset = UNSET
    robot_state: RobotState | Unset = UNSET
    robot_end_state: RobotEndState | Unset = UNSET
    errors: list[RobotError] | Unset = UNSET
    footprint: Footprint | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        robot_identity = self.robot_identity.to_dict()

        runtime_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.runtime_data, Unset):
            runtime_data = self.runtime_data.to_dict()

        robot_state: dict[str, Any] | Unset = UNSET
        if not isinstance(self.robot_state, Unset):
            robot_state = self.robot_state.to_dict()

        robot_end_state: str | Unset = UNSET
        if not isinstance(self.robot_end_state, Unset):
            robot_end_state = self.robot_end_state.value

        errors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item = errors_item_data.to_dict()
                errors.append(errors_item)

        footprint: dict[str, Any] | Unset = UNSET
        if not isinstance(self.footprint, Unset):
            footprint = self.footprint.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "robot-identity": robot_identity,
            }
        )
        if runtime_data is not UNSET:
            field_dict["runtime-data"] = runtime_data
        if robot_state is not UNSET:
            field_dict["robot-state"] = robot_state
        if robot_end_state is not UNSET:
            field_dict["robot-end-state"] = robot_end_state
        if errors is not UNSET:
            field_dict["errors"] = errors
        if footprint is not UNSET:
            field_dict["footprint"] = footprint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.footprint import Footprint
        from ..models.robot_error import RobotError
        from ..models.robot_identity import RobotIdentity
        from ..models.robot_runtime import RobotRuntime
        from ..models.robot_state import RobotState

        d = dict(src_dict)
        robot_identity = RobotIdentity.from_dict(d.pop("robot-identity"))

        _runtime_data = d.pop("runtime-data", UNSET)
        runtime_data: RobotRuntime | Unset
        if isinstance(_runtime_data, Unset):
            runtime_data = UNSET
        else:
            runtime_data = RobotRuntime.from_dict(_runtime_data)

        _robot_state = d.pop("robot-state", UNSET)
        robot_state: RobotState | Unset
        if isinstance(_robot_state, Unset):
            robot_state = UNSET
        else:
            robot_state = RobotState.from_dict(_robot_state)

        _robot_end_state = d.pop("robot-end-state", UNSET)
        robot_end_state: RobotEndState | Unset
        if isinstance(_robot_end_state, Unset):
            robot_end_state = UNSET
        else:
            robot_end_state = RobotEndState(_robot_end_state)

        _errors = d.pop("errors", UNSET)
        errors: list[RobotError] | Unset = UNSET
        if _errors is not UNSET:
            errors = []
            for errors_item_data in _errors:
                errors_item = RobotError.from_dict(errors_item_data)

                errors.append(errors_item)

        _footprint = d.pop("footprint", UNSET)
        footprint: Footprint | Unset
        if isinstance(_footprint, Unset):
            footprint = UNSET
        else:
            footprint = Footprint.from_dict(_footprint)

        robot_response = cls(
            robot_identity=robot_identity,
            runtime_data=runtime_data,
            robot_state=robot_state,
            robot_end_state=robot_end_state,
            errors=errors,
            footprint=footprint,
        )

        return robot_response
