from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_argument import MissionArgument


T = TypeVar("T", bound="Phase")


@_attrs_define
class Phase:
    """
    Attributes:
        mission_id (None | Unset | UUID):
        arguments (list[MissionArgument] | Unset):
        fallback_mission_id (None | Unset | UUID):
        order_id (None | Unset | UUID):
    """

    mission_id: None | Unset | UUID = UNSET
    arguments: list[MissionArgument] | Unset = UNSET
    fallback_mission_id: None | Unset | UUID = UNSET
    order_id: None | Unset | UUID = UNSET

    def to_dict(self) -> dict[str, Any]:
        mission_id: None | str | Unset
        if isinstance(self.mission_id, Unset):
            mission_id = UNSET
        elif isinstance(self.mission_id, UUID):
            mission_id = str(self.mission_id)
        else:
            mission_id = self.mission_id

        arguments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.arguments, Unset):
            arguments = []
            for arguments_item_data in self.arguments:
                arguments_item = arguments_item_data.to_dict()
                arguments.append(arguments_item)

        fallback_mission_id: None | str | Unset
        if isinstance(self.fallback_mission_id, Unset):
            fallback_mission_id = UNSET
        elif isinstance(self.fallback_mission_id, UUID):
            fallback_mission_id = str(self.fallback_mission_id)
        else:
            fallback_mission_id = self.fallback_mission_id

        order_id: None | str | Unset
        if isinstance(self.order_id, Unset):
            order_id = UNSET
        elif isinstance(self.order_id, UUID):
            order_id = str(self.order_id)
        else:
            order_id = self.order_id

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if mission_id is not UNSET:
            field_dict["mission-id"] = mission_id
        if arguments is not UNSET:
            field_dict["arguments"] = arguments
        if fallback_mission_id is not UNSET:
            field_dict["fallback-mission-id"] = fallback_mission_id
        if order_id is not UNSET:
            field_dict["order-id"] = order_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_argument import MissionArgument

        d = dict(src_dict)

        def _parse_mission_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                mission_id_type_0 = UUID(data)

                return mission_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        mission_id = _parse_mission_id(d.pop("mission-id", UNSET))

        _arguments = d.pop("arguments", UNSET)
        arguments: list[MissionArgument] | Unset = UNSET
        if _arguments is not UNSET:
            arguments = []
            for arguments_item_data in _arguments:
                arguments_item = MissionArgument.from_dict(arguments_item_data)

                arguments.append(arguments_item)

        def _parse_fallback_mission_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                fallback_mission_id_type_0 = UUID(data)

                return fallback_mission_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        fallback_mission_id = _parse_fallback_mission_id(d.pop("fallback-mission-id", UNSET))

        def _parse_order_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                order_id_type_0 = UUID(data)

                return order_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        order_id = _parse_order_id(d.pop("order-id", UNSET))

        phase = cls(
            mission_id=mission_id,
            arguments=arguments,
            fallback_mission_id=fallback_mission_id,
            order_id=order_id,
        )

        return phase
