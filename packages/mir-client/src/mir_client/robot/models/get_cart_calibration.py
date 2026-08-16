from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetCartCalibration")


@_attrs_define
class GetCartCalibration:
    """
    Attributes:
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        drive_height (int | Unset): The height of the hook when driving with carts of this cart calibration
        entry_height (int | Unset): The entry height of the hook for the cart calibration
        guid (str | Unset): The global id unique across robots that identifies this cart calibration
        lock_height (int | Unset): The lock height of the hook for the cart calibration
        name (str | Unset): The name of the cart calibration
        qw (float | Unset): The qw quaternion of the cart calibration
        qx (float | Unset): The qx quaternion of the cart calibration
        qy (float | Unset): The qy quaternion of the cart calibration
        qz (float | Unset): The qz quaternion of the cart calibration
        standard (bool | Unset): If the cart calibration is standard or not
        x (float | Unset): The offset in the x-coordinate of the cart calibration
        y (float | Unset): The offset in the y-coordinate of the cart calibration
        z (float | Unset): The offset in the z-coordinate of the cart calibration
    """

    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    drive_height: int | Unset = UNSET
    entry_height: int | Unset = UNSET
    guid: str | Unset = UNSET
    lock_height: int | Unset = UNSET
    name: str | Unset = UNSET
    qw: float | Unset = UNSET
    qx: float | Unset = UNSET
    qy: float | Unset = UNSET
    qz: float | Unset = UNSET
    standard: bool | Unset = UNSET
    x: float | Unset = UNSET
    y: float | Unset = UNSET
    z: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_by = self.created_by

        created_by_id = self.created_by_id

        drive_height = self.drive_height

        entry_height = self.entry_height

        guid = self.guid

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if drive_height is not UNSET:
            field_dict["drive_height"] = drive_height
        if entry_height is not UNSET:
            field_dict["entry_height"] = entry_height
        if guid is not UNSET:
            field_dict["guid"] = guid
        if lock_height is not UNSET:
            field_dict["lock_height"] = lock_height
        if name is not UNSET:
            field_dict["name"] = name
        if qw is not UNSET:
            field_dict["qw"] = qw
        if qx is not UNSET:
            field_dict["qx"] = qx
        if qy is not UNSET:
            field_dict["qy"] = qy
        if qz is not UNSET:
            field_dict["qz"] = qz
        if standard is not UNSET:
            field_dict["standard"] = standard
        if x is not UNSET:
            field_dict["x"] = x
        if y is not UNSET:
            field_dict["y"] = y
        if z is not UNSET:
            field_dict["z"] = z

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        drive_height = d.pop("drive_height", UNSET)

        entry_height = d.pop("entry_height", UNSET)

        guid = d.pop("guid", UNSET)

        lock_height = d.pop("lock_height", UNSET)

        name = d.pop("name", UNSET)

        qw = d.pop("qw", UNSET)

        qx = d.pop("qx", UNSET)

        qy = d.pop("qy", UNSET)

        qz = d.pop("qz", UNSET)

        standard = d.pop("standard", UNSET)

        x = d.pop("x", UNSET)

        y = d.pop("y", UNSET)

        z = d.pop("z", UNSET)

        get_cart_calibration = cls(
            created_by=created_by,
            created_by_id=created_by_id,
            drive_height=drive_height,
            entry_height=entry_height,
            guid=guid,
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
        )

        get_cart_calibration.additional_properties = d
        return get_cart_calibration

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
