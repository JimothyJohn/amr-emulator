from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.marker_type_1 import MarkerType1
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bar import Bar
    from ..models.pose import Pose


T = TypeVar("T", bound="Marker")


@_attrs_define
class Marker:
    """
    Attributes:
        type_ (str):
        map_id (UUID):
        name (str):
        map_pose (Pose):
        offset_pose (Pose):
        marker_type (MarkerType1):
        id (None | Unset | UUID):
        bar (Bar | Unset):
    """

    type_: str
    map_id: UUID
    name: str
    map_pose: Pose
    offset_pose: Pose
    marker_type: MarkerType1
    id: None | Unset | UUID = UNSET
    bar: Bar | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        map_id = str(self.map_id)

        name = self.name

        map_pose = self.map_pose.to_dict()

        offset_pose = self.offset_pose.to_dict()

        marker_type = self.marker_type.value

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        elif isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        bar: dict[str, Any] | Unset = UNSET
        if not isinstance(self.bar, Unset):
            bar = self.bar.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "map-id": map_id,
                "name": name,
                "map-pose": map_pose,
                "offset-pose": offset_pose,
                "marker-type": marker_type,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if bar is not UNSET:
            field_dict["bar"] = bar

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bar import Bar
        from ..models.pose import Pose

        d = dict(src_dict)
        type_ = d.pop("type")

        map_id = UUID(d.pop("map-id"))

        name = d.pop("name")

        map_pose = Pose.from_dict(d.pop("map-pose"))

        offset_pose = Pose.from_dict(d.pop("offset-pose"))

        marker_type = MarkerType1(d.pop("marker-type"))

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

        _bar = d.pop("bar", UNSET)
        bar: Bar | Unset
        if isinstance(_bar, Unset):
            bar = UNSET
        else:
            bar = Bar.from_dict(_bar)

        marker = cls(
            type_=type_,
            map_id=map_id,
            name=name,
            map_pose=map_pose,
            offset_pose=offset_pose,
            marker_type=marker_type,
            id=id,
            bar=bar,
        )

        marker.additional_properties = d
        return marker

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
