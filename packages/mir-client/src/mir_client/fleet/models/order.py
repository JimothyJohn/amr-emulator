from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.order_priority import OrderPriority
from ..models.order_status import OrderStatus
from ..models.order_type import OrderType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.order_action import OrderAction


T = TypeVar("T", bound="Order")


@_attrs_define
class Order:
    """
    Attributes:
        order_id (str):
        mission_name (str):
        order_type (OrderType | Unset):
        mission_id (None | str | Unset):
        mission_arguments (None | str | Unset):
        order_status (OrderStatus | Unset):
        order_created (datetime.datetime | Unset):
        order_queued (datetime.datetime | None | Unset):
        order_started (datetime.datetime | None | Unset):
        order_finished (datetime.datetime | None | Unset):
        robot_id (None | str | Unset):
        robot_name (None | str | Unset):
        order_priority (OrderPriority | Unset):
        user_guid (None | str | Unset):
        user_name (None | str | Unset):
        api_key_guid (None | str | Unset):
        api_key_name (None | str | Unset):
        actions (list[OrderAction] | Unset):
    """

    order_id: str
    mission_name: str
    order_type: OrderType | Unset = UNSET
    mission_id: None | str | Unset = UNSET
    mission_arguments: None | str | Unset = UNSET
    order_status: OrderStatus | Unset = UNSET
    order_created: datetime.datetime | Unset = UNSET
    order_queued: datetime.datetime | None | Unset = UNSET
    order_started: datetime.datetime | None | Unset = UNSET
    order_finished: datetime.datetime | None | Unset = UNSET
    robot_id: None | str | Unset = UNSET
    robot_name: None | str | Unset = UNSET
    order_priority: OrderPriority | Unset = UNSET
    user_guid: None | str | Unset = UNSET
    user_name: None | str | Unset = UNSET
    api_key_guid: None | str | Unset = UNSET
    api_key_name: None | str | Unset = UNSET
    actions: list[OrderAction] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        order_id = self.order_id

        mission_name = self.mission_name

        order_type: str | Unset = UNSET
        if not isinstance(self.order_type, Unset):
            order_type = self.order_type.value

        mission_id: None | str | Unset
        if isinstance(self.mission_id, Unset):
            mission_id = UNSET
        else:
            mission_id = self.mission_id

        mission_arguments: None | str | Unset
        if isinstance(self.mission_arguments, Unset):
            mission_arguments = UNSET
        else:
            mission_arguments = self.mission_arguments

        order_status: str | Unset = UNSET
        if not isinstance(self.order_status, Unset):
            order_status = self.order_status.value

        order_created: str | Unset = UNSET
        if not isinstance(self.order_created, Unset):
            order_created = self.order_created.isoformat()

        order_queued: None | str | Unset
        if isinstance(self.order_queued, Unset):
            order_queued = UNSET
        elif isinstance(self.order_queued, datetime.datetime):
            order_queued = self.order_queued.isoformat()
        else:
            order_queued = self.order_queued

        order_started: None | str | Unset
        if isinstance(self.order_started, Unset):
            order_started = UNSET
        elif isinstance(self.order_started, datetime.datetime):
            order_started = self.order_started.isoformat()
        else:
            order_started = self.order_started

        order_finished: None | str | Unset
        if isinstance(self.order_finished, Unset):
            order_finished = UNSET
        elif isinstance(self.order_finished, datetime.datetime):
            order_finished = self.order_finished.isoformat()
        else:
            order_finished = self.order_finished

        robot_id: None | str | Unset
        if isinstance(self.robot_id, Unset):
            robot_id = UNSET
        else:
            robot_id = self.robot_id

        robot_name: None | str | Unset
        if isinstance(self.robot_name, Unset):
            robot_name = UNSET
        else:
            robot_name = self.robot_name

        order_priority: str | Unset = UNSET
        if not isinstance(self.order_priority, Unset):
            order_priority = self.order_priority.value

        user_guid: None | str | Unset
        if isinstance(self.user_guid, Unset):
            user_guid = UNSET
        else:
            user_guid = self.user_guid

        user_name: None | str | Unset
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        api_key_guid: None | str | Unset
        if isinstance(self.api_key_guid, Unset):
            api_key_guid = UNSET
        else:
            api_key_guid = self.api_key_guid

        api_key_name: None | str | Unset
        if isinstance(self.api_key_name, Unset):
            api_key_name = UNSET
        else:
            api_key_name = self.api_key_name

        actions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for actions_item_data in self.actions:
                actions_item = actions_item_data.to_dict()
                actions.append(actions_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "order-id": order_id,
                "mission-name": mission_name,
            }
        )
        if order_type is not UNSET:
            field_dict["order-type"] = order_type
        if mission_id is not UNSET:
            field_dict["mission-id"] = mission_id
        if mission_arguments is not UNSET:
            field_dict["mission-arguments"] = mission_arguments
        if order_status is not UNSET:
            field_dict["order-status"] = order_status
        if order_created is not UNSET:
            field_dict["order-created"] = order_created
        if order_queued is not UNSET:
            field_dict["order-queued"] = order_queued
        if order_started is not UNSET:
            field_dict["order-started"] = order_started
        if order_finished is not UNSET:
            field_dict["order-finished"] = order_finished
        if robot_id is not UNSET:
            field_dict["robot-id"] = robot_id
        if robot_name is not UNSET:
            field_dict["robot-name"] = robot_name
        if order_priority is not UNSET:
            field_dict["order-priority"] = order_priority
        if user_guid is not UNSET:
            field_dict["user-guid"] = user_guid
        if user_name is not UNSET:
            field_dict["user-name"] = user_name
        if api_key_guid is not UNSET:
            field_dict["api-key-guid"] = api_key_guid
        if api_key_name is not UNSET:
            field_dict["api-key-name"] = api_key_name
        if actions is not UNSET:
            field_dict["actions"] = actions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.order_action import OrderAction

        d = dict(src_dict)
        order_id = d.pop("order-id")

        mission_name = d.pop("mission-name")

        _order_type = d.pop("order-type", UNSET)
        order_type: OrderType | Unset
        if isinstance(_order_type, Unset):
            order_type = UNSET
        else:
            order_type = OrderType(_order_type)

        def _parse_mission_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mission_id = _parse_mission_id(d.pop("mission-id", UNSET))

        def _parse_mission_arguments(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mission_arguments = _parse_mission_arguments(d.pop("mission-arguments", UNSET))

        _order_status = d.pop("order-status", UNSET)
        order_status: OrderStatus | Unset
        if isinstance(_order_status, Unset):
            order_status = UNSET
        else:
            order_status = OrderStatus(_order_status)

        _order_created = d.pop("order-created", UNSET)
        order_created: datetime.datetime | Unset
        if isinstance(_order_created, Unset):
            order_created = UNSET
        else:
            order_created = datetime.datetime.fromisoformat(_order_created)

        def _parse_order_queued(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                order_queued_type_0 = datetime.datetime.fromisoformat(data)

                return order_queued_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        order_queued = _parse_order_queued(d.pop("order-queued", UNSET))

        def _parse_order_started(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                order_started_type_0 = datetime.datetime.fromisoformat(data)

                return order_started_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        order_started = _parse_order_started(d.pop("order-started", UNSET))

        def _parse_order_finished(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                order_finished_type_0 = datetime.datetime.fromisoformat(data)

                return order_finished_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        order_finished = _parse_order_finished(d.pop("order-finished", UNSET))

        def _parse_robot_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        robot_id = _parse_robot_id(d.pop("robot-id", UNSET))

        def _parse_robot_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        robot_name = _parse_robot_name(d.pop("robot-name", UNSET))

        _order_priority = d.pop("order-priority", UNSET)
        order_priority: OrderPriority | Unset
        if isinstance(_order_priority, Unset):
            order_priority = UNSET
        else:
            order_priority = OrderPriority(_order_priority)

        def _parse_user_guid(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_guid = _parse_user_guid(d.pop("user-guid", UNSET))

        def _parse_user_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_name = _parse_user_name(d.pop("user-name", UNSET))

        def _parse_api_key_guid(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_key_guid = _parse_api_key_guid(d.pop("api-key-guid", UNSET))

        def _parse_api_key_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_key_name = _parse_api_key_name(d.pop("api-key-name", UNSET))

        _actions = d.pop("actions", UNSET)
        actions: list[OrderAction] | Unset = UNSET
        if _actions is not UNSET:
            actions = []
            for actions_item_data in _actions:
                actions_item = OrderAction.from_dict(actions_item_data)

                actions.append(actions_item)

        order = cls(
            order_id=order_id,
            mission_name=mission_name,
            order_type=order_type,
            mission_id=mission_id,
            mission_arguments=mission_arguments,
            order_status=order_status,
            order_created=order_created,
            order_queued=order_queued,
            order_started=order_started,
            order_finished=order_finished,
            robot_id=robot_id,
            robot_name=robot_name,
            order_priority=order_priority,
            user_guid=user_guid,
            user_name=user_name,
            api_key_guid=api_key_guid,
            api_key_name=api_key_name,
            actions=actions,
        )

        return order
