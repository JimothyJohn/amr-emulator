from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.zone_event_address import ZoneEventAddress
from ..models.zone_event_type import ZoneEventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.io_parameters import IoParameters
    from ..models.plc_parameters import PlcParameters
    from ..models.zone_event_event import ZoneEventEvent


T = TypeVar("T", bound="ZoneEvent")


@_attrs_define
class ZoneEvent:
    """
    Attributes:
        name (str):
        event (ZoneEventEvent):
        type_ (ZoneEventType):
        address (ZoneEventAddress):
        plc_parameters (PlcParameters | Unset):
        io_parameters (IoParameters | Unset):
    """

    name: str
    event: ZoneEventEvent
    type_: ZoneEventType
    address: ZoneEventAddress
    plc_parameters: PlcParameters | Unset = UNSET
    io_parameters: IoParameters | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        event = self.event.to_dict()

        type_ = self.type_.value

        address = self.address.value

        plc_parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.plc_parameters, Unset):
            plc_parameters = self.plc_parameters.to_dict()

        io_parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.io_parameters, Unset):
            io_parameters = self.io_parameters.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "event": event,
                "type": type_,
                "address": address,
            }
        )
        if plc_parameters is not UNSET:
            field_dict["plc-parameters"] = plc_parameters
        if io_parameters is not UNSET:
            field_dict["io-parameters"] = io_parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.io_parameters import IoParameters
        from ..models.plc_parameters import PlcParameters
        from ..models.zone_event_event import ZoneEventEvent

        d = dict(src_dict)
        name = d.pop("name")

        event = ZoneEventEvent.from_dict(d.pop("event"))

        type_ = ZoneEventType(d.pop("type"))

        address = ZoneEventAddress(d.pop("address"))

        _plc_parameters = d.pop("plc-parameters", UNSET)
        plc_parameters: PlcParameters | Unset
        if isinstance(_plc_parameters, Unset):
            plc_parameters = UNSET
        else:
            plc_parameters = PlcParameters.from_dict(_plc_parameters)

        _io_parameters = d.pop("io-parameters", UNSET)
        io_parameters: IoParameters | Unset
        if isinstance(_io_parameters, Unset):
            io_parameters = UNSET
        else:
            io_parameters = IoParameters.from_dict(_io_parameters)

        zone_event = cls(
            name=name,
            event=event,
            type_=type_,
            address=address,
            plc_parameters=plc_parameters,
            io_parameters=io_parameters,
        )

        return zone_event
