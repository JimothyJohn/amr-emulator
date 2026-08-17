from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostDockingOffsets")


@_attrs_define
class PostDockingOffsets:
    """
    Attributes:
        name (str): Min length: 1, Max length: 255
        orientation_offset (float):
        x_offset (float):
        y_offset (float):
        created_by_id (str | Unset):
        docking_type (int | Unset):
        guid (str | Unset):
        pos_id (str | Unset):
    """

    name: str
    orientation_offset: float
    x_offset: float
    y_offset: float
    created_by_id: str | Unset = UNSET
    docking_type: int | Unset = UNSET
    guid: str | Unset = UNSET
    pos_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        orientation_offset = self.orientation_offset

        x_offset = self.x_offset

        y_offset = self.y_offset

        created_by_id = self.created_by_id

        docking_type = self.docking_type

        guid = self.guid

        pos_id = self.pos_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "orientation_offset": orientation_offset,
                "x_offset": x_offset,
                "y_offset": y_offset,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if docking_type is not UNSET:
            field_dict["docking_type"] = docking_type
        if guid is not UNSET:
            field_dict["guid"] = guid
        if pos_id is not UNSET:
            field_dict["pos_id"] = pos_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        orientation_offset = d.pop("orientation_offset")

        x_offset = d.pop("x_offset")

        y_offset = d.pop("y_offset")

        created_by_id = d.pop("created_by_id", UNSET)

        docking_type = d.pop("docking_type", UNSET)

        guid = d.pop("guid", UNSET)

        pos_id = d.pop("pos_id", UNSET)

        post_docking_offsets = cls(
            name=name,
            orientation_offset=orientation_offset,
            x_offset=x_offset,
            y_offset=y_offset,
            created_by_id=created_by_id,
            docking_type=docking_type,
            guid=guid,
            pos_id=pos_id,
        )

        post_docking_offsets.additional_properties = d
        return post_docking_offsets

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
