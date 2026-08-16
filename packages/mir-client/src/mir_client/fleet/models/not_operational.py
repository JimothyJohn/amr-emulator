from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error import Error
    from ..models.external_cable_charger_connected import ExternalCableChargerConnected
    from ..models.key import Key
    from ..models.manual_control import ManualControl
    from ..models.paused import Paused
    from ..models.safety_stop import SafetyStop
    from ..models.system_busy import SystemBusy


T = TypeVar("T", bound="NotOperational")


@_attrs_define
class NotOperational:
    """
    Attributes:
        manual_control (ManualControl | Unset):
        error (Error | Unset):
        paused (Paused | Unset):
        safety_stop (SafetyStop | Unset):
        system_busy (SystemBusy | Unset):
        key (Key | Unset):
        external_cable_charger_connected (ExternalCableChargerConnected | Unset):
    """

    manual_control: ManualControl | Unset = UNSET
    error: Error | Unset = UNSET
    paused: Paused | Unset = UNSET
    safety_stop: SafetyStop | Unset = UNSET
    system_busy: SystemBusy | Unset = UNSET
    key: Key | Unset = UNSET
    external_cable_charger_connected: ExternalCableChargerConnected | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        manual_control: dict[str, Any] | Unset = UNSET
        if not isinstance(self.manual_control, Unset):
            manual_control = self.manual_control.to_dict()

        error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        paused: dict[str, Any] | Unset = UNSET
        if not isinstance(self.paused, Unset):
            paused = self.paused.to_dict()

        safety_stop: dict[str, Any] | Unset = UNSET
        if not isinstance(self.safety_stop, Unset):
            safety_stop = self.safety_stop.to_dict()

        system_busy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.system_busy, Unset):
            system_busy = self.system_busy.to_dict()

        key: dict[str, Any] | Unset = UNSET
        if not isinstance(self.key, Unset):
            key = self.key.to_dict()

        external_cable_charger_connected: dict[str, Any] | Unset = UNSET
        if not isinstance(self.external_cable_charger_connected, Unset):
            external_cable_charger_connected = self.external_cable_charger_connected.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if manual_control is not UNSET:
            field_dict["manual-control"] = manual_control
        if error is not UNSET:
            field_dict["error"] = error
        if paused is not UNSET:
            field_dict["paused"] = paused
        if safety_stop is not UNSET:
            field_dict["safety-stop"] = safety_stop
        if system_busy is not UNSET:
            field_dict["system-busy"] = system_busy
        if key is not UNSET:
            field_dict["key"] = key
        if external_cable_charger_connected is not UNSET:
            field_dict["external-cable-charger-connected"] = external_cable_charger_connected

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error import Error
        from ..models.external_cable_charger_connected import ExternalCableChargerConnected
        from ..models.key import Key
        from ..models.manual_control import ManualControl
        from ..models.paused import Paused
        from ..models.safety_stop import SafetyStop
        from ..models.system_busy import SystemBusy

        d = dict(src_dict)
        _manual_control = d.pop("manual-control", UNSET)
        manual_control: ManualControl | Unset
        if isinstance(_manual_control, Unset):
            manual_control = UNSET
        else:
            manual_control = ManualControl.from_dict(_manual_control)

        _error = d.pop("error", UNSET)
        error: Error | Unset
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = Error.from_dict(_error)

        _paused = d.pop("paused", UNSET)
        paused: Paused | Unset
        if isinstance(_paused, Unset):
            paused = UNSET
        else:
            paused = Paused.from_dict(_paused)

        _safety_stop = d.pop("safety-stop", UNSET)
        safety_stop: SafetyStop | Unset
        if isinstance(_safety_stop, Unset):
            safety_stop = UNSET
        else:
            safety_stop = SafetyStop.from_dict(_safety_stop)

        _system_busy = d.pop("system-busy", UNSET)
        system_busy: SystemBusy | Unset
        if isinstance(_system_busy, Unset):
            system_busy = UNSET
        else:
            system_busy = SystemBusy.from_dict(_system_busy)

        _key = d.pop("key", UNSET)
        key: Key | Unset
        if isinstance(_key, Unset):
            key = UNSET
        else:
            key = Key.from_dict(_key)

        _external_cable_charger_connected = d.pop("external-cable-charger-connected", UNSET)
        external_cable_charger_connected: ExternalCableChargerConnected | Unset
        if isinstance(_external_cable_charger_connected, Unset):
            external_cable_charger_connected = UNSET
        else:
            external_cable_charger_connected = ExternalCableChargerConnected.from_dict(
                _external_cable_charger_connected
            )

        not_operational = cls(
            manual_control=manual_control,
            error=error,
            paused=paused,
            safety_stop=safety_stop,
            system_busy=system_busy,
            key=key,
            external_cable_charger_connected=external_cable_charger_connected,
        )

        return not_operational
