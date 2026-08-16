from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.point import Point


T = TypeVar("T", bound="Map1")


@_attrs_define
class Map1:
    """
    Attributes:
        name (str | Unset):
        image (str | Unset):
        origin (Point | Unset):
    """

    name: str | Unset = UNSET
    image: str | Unset = UNSET
    origin: Point | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        image = self.image

        origin: dict[str, Any] | Unset = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if image is not UNSET:
            field_dict["image"] = image
        if origin is not UNSET:
            field_dict["origin"] = origin

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.point import Point

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        image = d.pop("image", UNSET)

        _origin = d.pop("origin", UNSET)
        origin: Point | Unset
        if isinstance(_origin, Unset):
            origin = UNSET
        else:
            origin = Point.from_dict(_origin)

        map_1 = cls(
            name=name,
            image=image,
            origin=origin,
        )

        return map_1
