from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_status_errors_item import GetStatusErrorsItem
    from ..models.get_status_hook_data import GetStatusHookData
    from ..models.get_status_hook_status import GetStatusHookStatus
    from ..models.get_status_position import GetStatusPosition
    from ..models.get_status_user_prompt import GetStatusUserPrompt
    from ..models.get_status_velocity import GetStatusVelocity


T = TypeVar("T", bound="GetStatus")


@_attrs_define
class GetStatus:
    """
    Attributes:
        battery_percentage (float | Unset): The current charge percentage of the battery
        battery_time_remaining (int | Unset): The approximate time remaining on the battery during normal operation of
            the robot
        distance_to_next_target (float | Unset): The distance to the next target of the robot
        errors (list[GetStatusErrorsItem] | Unset): The list of actions executed as part of the mission
        footprint (str | Unset): The current footprint of the robot
        hook_data (GetStatusHookData | Unset):
        hook_status (GetStatusHookStatus | Unset):
        joystick_low_speed_mode_enabled (bool | Unset):
        joystick_web_session_id (str | Unset): The id of the web user that has control over the joystick
        map_id (str | Unset): The id of the current map the robot recides in
        mission_queue_id (int | Unset): The id of the current job the robot executes
        mission_queue_url (str | Unset): The url to the active mission in queue
        mission_text (str | Unset): Status message from mission controller
        mode_id (int | Unset): The id of the current mode of the robot
        mode_key_state (str | Unset): A textual description of the position of the mode key
        mode_text (str | Unset): A textual description of the current state of the robot
        moved (float | Unset):
        position (GetStatusPosition | Unset):
        robot_model (str | Unset): The model of the robot
        robot_name (str | Unset): The name of the robot
        safety_system_muted (bool | Unset):
        serial_number (str | Unset): The model of the robot
        session_id (str | Unset): The id of the session the robot recides in
        state_id (int | Unset): The id of the current state of the robot
        state_text (str | Unset): A textual description of the current state of the robot
        unloaded_map_changes (bool | Unset):
        uptime (int | Unset): The uptime of the robot
        user_prompt (GetStatusUserPrompt | Unset):
        velocity (GetStatusVelocity | Unset):
    """

    battery_percentage: float | Unset = UNSET
    battery_time_remaining: int | Unset = UNSET
    distance_to_next_target: float | Unset = UNSET
    errors: list[GetStatusErrorsItem] | Unset = UNSET
    footprint: str | Unset = UNSET
    hook_data: GetStatusHookData | Unset = UNSET
    hook_status: GetStatusHookStatus | Unset = UNSET
    joystick_low_speed_mode_enabled: bool | Unset = UNSET
    joystick_web_session_id: str | Unset = UNSET
    map_id: str | Unset = UNSET
    mission_queue_id: int | Unset = UNSET
    mission_queue_url: str | Unset = UNSET
    mission_text: str | Unset = UNSET
    mode_id: int | Unset = UNSET
    mode_key_state: str | Unset = UNSET
    mode_text: str | Unset = UNSET
    moved: float | Unset = UNSET
    position: GetStatusPosition | Unset = UNSET
    robot_model: str | Unset = UNSET
    robot_name: str | Unset = UNSET
    safety_system_muted: bool | Unset = UNSET
    serial_number: str | Unset = UNSET
    session_id: str | Unset = UNSET
    state_id: int | Unset = UNSET
    state_text: str | Unset = UNSET
    unloaded_map_changes: bool | Unset = UNSET
    uptime: int | Unset = UNSET
    user_prompt: GetStatusUserPrompt | Unset = UNSET
    velocity: GetStatusVelocity | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        battery_percentage = self.battery_percentage

        battery_time_remaining = self.battery_time_remaining

        distance_to_next_target = self.distance_to_next_target

        errors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item = errors_item_data.to_dict()
                errors.append(errors_item)

        footprint = self.footprint

        hook_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hook_data, Unset):
            hook_data = self.hook_data.to_dict()

        hook_status: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hook_status, Unset):
            hook_status = self.hook_status.to_dict()

        joystick_low_speed_mode_enabled = self.joystick_low_speed_mode_enabled

        joystick_web_session_id = self.joystick_web_session_id

        map_id = self.map_id

        mission_queue_id = self.mission_queue_id

        mission_queue_url = self.mission_queue_url

        mission_text = self.mission_text

        mode_id = self.mode_id

        mode_key_state = self.mode_key_state

        mode_text = self.mode_text

        moved = self.moved

        position: dict[str, Any] | Unset = UNSET
        if not isinstance(self.position, Unset):
            position = self.position.to_dict()

        robot_model = self.robot_model

        robot_name = self.robot_name

        safety_system_muted = self.safety_system_muted

        serial_number = self.serial_number

        session_id = self.session_id

        state_id = self.state_id

        state_text = self.state_text

        unloaded_map_changes = self.unloaded_map_changes

        uptime = self.uptime

        user_prompt: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_prompt, Unset):
            user_prompt = self.user_prompt.to_dict()

        velocity: dict[str, Any] | Unset = UNSET
        if not isinstance(self.velocity, Unset):
            velocity = self.velocity.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if battery_percentage is not UNSET:
            field_dict["battery_percentage"] = battery_percentage
        if battery_time_remaining is not UNSET:
            field_dict["battery_time_remaining"] = battery_time_remaining
        if distance_to_next_target is not UNSET:
            field_dict["distance_to_next_target"] = distance_to_next_target
        if errors is not UNSET:
            field_dict["errors"] = errors
        if footprint is not UNSET:
            field_dict["footprint"] = footprint
        if hook_data is not UNSET:
            field_dict["hook_data"] = hook_data
        if hook_status is not UNSET:
            field_dict["hook_status"] = hook_status
        if joystick_low_speed_mode_enabled is not UNSET:
            field_dict["joystick_low_speed_mode_enabled"] = joystick_low_speed_mode_enabled
        if joystick_web_session_id is not UNSET:
            field_dict["joystick_web_session_id"] = joystick_web_session_id
        if map_id is not UNSET:
            field_dict["map_id"] = map_id
        if mission_queue_id is not UNSET:
            field_dict["mission_queue_id"] = mission_queue_id
        if mission_queue_url is not UNSET:
            field_dict["mission_queue_url"] = mission_queue_url
        if mission_text is not UNSET:
            field_dict["mission_text"] = mission_text
        if mode_id is not UNSET:
            field_dict["mode_id"] = mode_id
        if mode_key_state is not UNSET:
            field_dict["mode_key_state"] = mode_key_state
        if mode_text is not UNSET:
            field_dict["mode_text"] = mode_text
        if moved is not UNSET:
            field_dict["moved"] = moved
        if position is not UNSET:
            field_dict["position"] = position
        if robot_model is not UNSET:
            field_dict["robot_model"] = robot_model
        if robot_name is not UNSET:
            field_dict["robot_name"] = robot_name
        if safety_system_muted is not UNSET:
            field_dict["safety_system_muted"] = safety_system_muted
        if serial_number is not UNSET:
            field_dict["serial_number"] = serial_number
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if state_id is not UNSET:
            field_dict["state_id"] = state_id
        if state_text is not UNSET:
            field_dict["state_text"] = state_text
        if unloaded_map_changes is not UNSET:
            field_dict["unloaded_map_changes"] = unloaded_map_changes
        if uptime is not UNSET:
            field_dict["uptime"] = uptime
        if user_prompt is not UNSET:
            field_dict["user_prompt"] = user_prompt
        if velocity is not UNSET:
            field_dict["velocity"] = velocity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_status_errors_item import GetStatusErrorsItem
        from ..models.get_status_hook_data import GetStatusHookData
        from ..models.get_status_hook_status import GetStatusHookStatus
        from ..models.get_status_position import GetStatusPosition
        from ..models.get_status_user_prompt import GetStatusUserPrompt
        from ..models.get_status_velocity import GetStatusVelocity

        d = dict(src_dict)
        battery_percentage = d.pop("battery_percentage", UNSET)

        battery_time_remaining = d.pop("battery_time_remaining", UNSET)

        distance_to_next_target = d.pop("distance_to_next_target", UNSET)

        _errors = d.pop("errors", UNSET)
        errors: list[GetStatusErrorsItem] | Unset = UNSET
        if _errors is not UNSET:
            errors = []
            for errors_item_data in _errors:
                errors_item = GetStatusErrorsItem.from_dict(errors_item_data)

                errors.append(errors_item)

        footprint = d.pop("footprint", UNSET)

        _hook_data = d.pop("hook_data", UNSET)
        hook_data: GetStatusHookData | Unset
        if isinstance(_hook_data, Unset):
            hook_data = UNSET
        else:
            hook_data = GetStatusHookData.from_dict(_hook_data)

        _hook_status = d.pop("hook_status", UNSET)
        hook_status: GetStatusHookStatus | Unset
        if isinstance(_hook_status, Unset):
            hook_status = UNSET
        else:
            hook_status = GetStatusHookStatus.from_dict(_hook_status)

        joystick_low_speed_mode_enabled = d.pop("joystick_low_speed_mode_enabled", UNSET)

        joystick_web_session_id = d.pop("joystick_web_session_id", UNSET)

        map_id = d.pop("map_id", UNSET)

        mission_queue_id = d.pop("mission_queue_id", UNSET)

        mission_queue_url = d.pop("mission_queue_url", UNSET)

        mission_text = d.pop("mission_text", UNSET)

        mode_id = d.pop("mode_id", UNSET)

        mode_key_state = d.pop("mode_key_state", UNSET)

        mode_text = d.pop("mode_text", UNSET)

        moved = d.pop("moved", UNSET)

        _position = d.pop("position", UNSET)
        position: GetStatusPosition | Unset
        if isinstance(_position, Unset):
            position = UNSET
        else:
            position = GetStatusPosition.from_dict(_position)

        robot_model = d.pop("robot_model", UNSET)

        robot_name = d.pop("robot_name", UNSET)

        safety_system_muted = d.pop("safety_system_muted", UNSET)

        serial_number = d.pop("serial_number", UNSET)

        session_id = d.pop("session_id", UNSET)

        state_id = d.pop("state_id", UNSET)

        state_text = d.pop("state_text", UNSET)

        unloaded_map_changes = d.pop("unloaded_map_changes", UNSET)

        uptime = d.pop("uptime", UNSET)

        _user_prompt = d.pop("user_prompt", UNSET)
        user_prompt: GetStatusUserPrompt | Unset
        if isinstance(_user_prompt, Unset):
            user_prompt = UNSET
        else:
            user_prompt = GetStatusUserPrompt.from_dict(_user_prompt)

        _velocity = d.pop("velocity", UNSET)
        velocity: GetStatusVelocity | Unset
        if isinstance(_velocity, Unset):
            velocity = UNSET
        else:
            velocity = GetStatusVelocity.from_dict(_velocity)

        get_status = cls(
            battery_percentage=battery_percentage,
            battery_time_remaining=battery_time_remaining,
            distance_to_next_target=distance_to_next_target,
            errors=errors,
            footprint=footprint,
            hook_data=hook_data,
            hook_status=hook_status,
            joystick_low_speed_mode_enabled=joystick_low_speed_mode_enabled,
            joystick_web_session_id=joystick_web_session_id,
            map_id=map_id,
            mission_queue_id=mission_queue_id,
            mission_queue_url=mission_queue_url,
            mission_text=mission_text,
            mode_id=mode_id,
            mode_key_state=mode_key_state,
            mode_text=mode_text,
            moved=moved,
            position=position,
            robot_model=robot_model,
            robot_name=robot_name,
            safety_system_muted=safety_system_muted,
            serial_number=serial_number,
            session_id=session_id,
            state_id=state_id,
            state_text=state_text,
            unloaded_map_changes=unloaded_map_changes,
            uptime=uptime,
            user_prompt=user_prompt,
            velocity=velocity,
        )

        get_status.additional_properties = d
        return get_status

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
