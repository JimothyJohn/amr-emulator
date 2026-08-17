from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_modbus_missions_parameters_item import PostModbusMissionsParametersItem


T = TypeVar("T", bound="PostModbusMissions")


@_attrs_define
class PostModbusMissions:
    """
    Attributes:
        coil_id (int):
        mission_id (str):
        name (str): Min length: 1, Max length: 200
        created_by_id (str | Unset):
        guid (str | Unset):
        parameters (list[PostModbusMissionsParametersItem] | Unset):
    """

    coil_id: int
    mission_id: str
    name: str
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    parameters: list[PostModbusMissionsParametersItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        coil_id = self.coil_id

        mission_id = self.mission_id

        name = self.name

        created_by_id = self.created_by_id

        guid = self.guid

        parameters: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = []
            for parameters_item_data in self.parameters:
                parameters_item = parameters_item_data.to_dict()
                parameters.append(parameters_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "coil_id": coil_id,
                "mission_id": mission_id,
                "name": name,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_modbus_missions_parameters_item import PostModbusMissionsParametersItem

        d = dict(src_dict)
        coil_id = d.pop("coil_id")

        mission_id = d.pop("mission_id")

        name = d.pop("name")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: list[PostModbusMissionsParametersItem] | Unset = UNSET
        if _parameters is not UNSET:
            parameters = []
            for parameters_item_data in _parameters:
                parameters_item = PostModbusMissionsParametersItem.from_dict(parameters_item_data)

                parameters.append(parameters_item)

        post_modbus_missions = cls(
            coil_id=coil_id,
            mission_id=mission_id,
            name=name,
            created_by_id=created_by_id,
            guid=guid,
            parameters=parameters,
        )

        post_modbus_missions.additional_properties = d
        return post_modbus_missions

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
