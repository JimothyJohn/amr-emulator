from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostCartCalibrations")


@_attrs_define
class PostCartCalibrations:
    """
    Attributes:
        drive_height (int):
        entry_height (int):
        lock_height (int):
        name (str): Min length: 1, Max length: 40
        qw (float):
        qx (float):
        qy (float):
        qz (float):
        standard (bool):
        x (float):
        y (float):
        z (float):
        created_by_id (str | Unset):
        guid (str | Unset):
    """

    drive_height: int
    entry_height: int
    lock_height: int
    name: str
    qw: float
    qx: float
    qy: float
    qz: float
    standard: bool
    x: float
    y: float
    z: float
    created_by_id: str | Unset = UNSET
    guid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        drive_height = self.drive_height

        entry_height = self.entry_height

        lock_height = self.lock_height

        name = self.name

        qw = self.qw

        qx = self.qx

        qy = self.qy

        qz = self.qz

        standard = self.standard

        x = self.x

        y = self.y

        z = self.z

        created_by_id = self.created_by_id

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "drive_height": drive_height,
                "entry_height": entry_height,
                "lock_height": lock_height,
                "name": name,
                "qw": qw,
                "qx": qx,
                "qy": qy,
                "qz": qz,
                "standard": standard,
                "x": x,
                "y": y,
                "z": z,
            }
        )
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        drive_height = d.pop("drive_height")

        entry_height = d.pop("entry_height")

        lock_height = d.pop("lock_height")

        name = d.pop("name")

        qw = d.pop("qw")

        qx = d.pop("qx")

        qy = d.pop("qy")

        qz = d.pop("qz")

        standard = d.pop("standard")

        x = d.pop("x")

        y = d.pop("y")

        z = d.pop("z")

        created_by_id = d.pop("created_by_id", UNSET)

        guid = d.pop("guid", UNSET)

        post_cart_calibrations = cls(
            drive_height=drive_height,
            entry_height=entry_height,
            lock_height=lock_height,
            name=name,
            qw=qw,
            qx=qx,
            qy=qy,
            qz=qz,
            standard=standard,
            x=x,
            y=y,
            z=z,
            created_by_id=created_by_id,
            guid=guid,
        )

        post_cart_calibrations.additional_properties = d
        return post_cart_calibrations

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
