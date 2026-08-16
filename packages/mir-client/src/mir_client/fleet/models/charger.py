from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.charger_type import ChargerType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pose import Pose


T = TypeVar("T", bound="Charger")


@_attrs_define
class Charger:
    """
    Attributes:
        type_ (str):
        map_id (UUID):
        name (str):
        map_pose (Pose):
        charger_type (ChargerType):
        id (None | Unset | UUID):
    """

    type_: str
    map_id: UUID
    name: str
    map_pose: Pose
    charger_type: ChargerType
    id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        map_id = str(self.map_id)

        name = self.name

        map_pose = self.map_pose.to_dict()

        charger_type = self.charger_type.value

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        elif isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "map-id": map_id,
                "name": name,
                "map-pose": map_pose,
                "charger-type": charger_type,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pose import Pose

        d = dict(src_dict)
        type_ = d.pop("type")

        map_id = UUID(d.pop("map-id"))

        name = d.pop("name")

        map_pose = Pose.from_dict(d.pop("map-pose"))

        charger_type = ChargerType(d.pop("charger-type"))

        def _parse_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                id_type_0 = UUID(data)

                return id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        id = _parse_id(d.pop("id", UNSET))

        charger = cls(
            type_=type_,
            map_id=map_id,
            name=name,
            map_pose=map_pose,
            charger_type=charger_type,
            id=id,
        )

        charger.additional_properties = d
        return charger

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
