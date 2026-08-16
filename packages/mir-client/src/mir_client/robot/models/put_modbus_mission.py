from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.put_modbus_mission_parameters_item import PutModbusMissionParametersItem


T = TypeVar("T", bound="PutModbusMission")


@_attrs_define
class PutModbusMission:
    """
    Attributes:
        coil_id (int | Unset):
        mission_id (str | Unset):
        name (str | Unset): Min length: 1, Max length: 200
        parameters (list[PutModbusMissionParametersItem] | Unset):
    """

    coil_id: int | Unset = UNSET
    mission_id: str | Unset = UNSET
    name: str | Unset = UNSET
    parameters: list[PutModbusMissionParametersItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        coil_id = self.coil_id

        mission_id = self.mission_id

        name = self.name

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if coil_id is not UNSET:
            field_dict["coil_id"] = coil_id
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id
        if name is not UNSET:
            field_dict["name"] = name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.put_modbus_mission_parameters_item import PutModbusMissionParametersItem

        d = dict(src_dict)
        coil_id = d.pop("coil_id", UNSET)

        mission_id = d.pop("mission_id", UNSET)

        name = d.pop("name", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: list[PutModbusMissionParametersItem] | Unset = UNSET
        if _parameters is not UNSET:
            parameters = []
            for parameters_item_data in _parameters:
                parameters_item = PutModbusMissionParametersItem.from_dict(parameters_item_data)

                parameters.append(parameters_item)

        put_modbus_mission = cls(
            coil_id=coil_id,
            mission_id=mission_id,
            name=name,
            parameters=parameters,
        )

        put_modbus_mission.additional_properties = d
        return put_modbus_mission

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
