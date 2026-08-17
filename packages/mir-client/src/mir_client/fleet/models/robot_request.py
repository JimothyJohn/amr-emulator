from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.requested_robot_end_state import RequestedRobotEndState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.robot_error import RobotError


T = TypeVar("T", bound="RobotRequest")


@_attrs_define
class RobotRequest:
    """
    Attributes:
        robot_end_state (RequestedRobotEndState | Unset):
        errors (list[RobotError] | None | Unset):
    """

    robot_end_state: RequestedRobotEndState | Unset = UNSET
    errors: list[RobotError] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        robot_end_state: str | Unset = UNSET
        if not isinstance(self.robot_end_state, Unset):
            robot_end_state = self.robot_end_state.value

        errors: list[dict[str, Any]] | None | Unset
        if isinstance(self.errors, Unset):
            errors = UNSET
        elif isinstance(self.errors, list):
            errors = []
            for errors_type_0_item_data in self.errors:
                errors_type_0_item = errors_type_0_item_data.to_dict()
                errors.append(errors_type_0_item)

        else:
            errors = self.errors

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if robot_end_state is not UNSET:
            field_dict["robot-end-state"] = robot_end_state
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.robot_error import RobotError

        d = dict(src_dict)
        _robot_end_state = d.pop("robot-end-state", UNSET)
        robot_end_state: RequestedRobotEndState | Unset
        if isinstance(_robot_end_state, Unset):
            robot_end_state = UNSET
        else:
            robot_end_state = RequestedRobotEndState(_robot_end_state)

        def _parse_errors(data: object) -> list[RobotError] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                errors_type_0 = []
                _errors_type_0 = data
                for errors_type_0_item_data in _errors_type_0:
                    errors_type_0_item = RobotError.from_dict(errors_type_0_item_data)

                    errors_type_0.append(errors_type_0_item)

                return errors_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[RobotError] | None | Unset, data)

        errors = _parse_errors(d.pop("errors", UNSET))

        robot_request = cls(
            robot_end_state=robot_end_state,
            errors=errors,
        )

        return robot_request
