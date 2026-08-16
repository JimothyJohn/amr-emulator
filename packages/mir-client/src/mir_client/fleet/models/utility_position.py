from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pallet_docking_option import PalletDockingOption
from ..models.utility_position_type import UtilityPositionType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bar import Bar
    from ..models.deep_lane_setting import DeepLaneSetting
    from ..models.elevation import Elevation
    from ..models.pose import Pose


T = TypeVar("T", bound="UtilityPosition")


@_attrs_define
class UtilityPosition:
    """
    Attributes:
        type_ (str):
        map_id (UUID):
        name (str):
        map_pose (Pose):
        utility_position_type (UtilityPositionType):
        pallet_docking_option (PalletDockingOption):
        id (None | Unset | UUID):
        offset_pose (Pose | Unset):
        bar (Bar | Unset):
        elevation (Elevation | Unset):
        deep_lane_setting (DeepLaneSetting | Unset):
        place_offset_pose (Pose | Unset):
        load_jam_detection_enabled (bool | None | Unset):
    """

    type_: str
    map_id: UUID
    name: str
    map_pose: Pose
    utility_position_type: UtilityPositionType
    pallet_docking_option: PalletDockingOption
    id: None | Unset | UUID = UNSET
    offset_pose: Pose | Unset = UNSET
    bar: Bar | Unset = UNSET
    elevation: Elevation | Unset = UNSET
    deep_lane_setting: DeepLaneSetting | Unset = UNSET
    place_offset_pose: Pose | Unset = UNSET
    load_jam_detection_enabled: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        map_id = str(self.map_id)

        name = self.name

        map_pose = self.map_pose.to_dict()

        utility_position_type = self.utility_position_type.value

        pallet_docking_option = self.pallet_docking_option.value

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        elif isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        offset_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.offset_pose, Unset):
            offset_pose = self.offset_pose.to_dict()

        bar: dict[str, Any] | Unset = UNSET
        if not isinstance(self.bar, Unset):
            bar = self.bar.to_dict()

        elevation: dict[str, Any] | Unset = UNSET
        if not isinstance(self.elevation, Unset):
            elevation = self.elevation.to_dict()

        deep_lane_setting: dict[str, Any] | Unset = UNSET
        if not isinstance(self.deep_lane_setting, Unset):
            deep_lane_setting = self.deep_lane_setting.to_dict()

        place_offset_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.place_offset_pose, Unset):
            place_offset_pose = self.place_offset_pose.to_dict()

        load_jam_detection_enabled: bool | None | Unset
        if isinstance(self.load_jam_detection_enabled, Unset):
            load_jam_detection_enabled = UNSET
        else:
            load_jam_detection_enabled = self.load_jam_detection_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "map-id": map_id,
                "name": name,
                "map-pose": map_pose,
                "utility-position-type": utility_position_type,
                "pallet-docking-option": pallet_docking_option,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if offset_pose is not UNSET:
            field_dict["offset-pose"] = offset_pose
        if bar is not UNSET:
            field_dict["bar"] = bar
        if elevation is not UNSET:
            field_dict["elevation"] = elevation
        if deep_lane_setting is not UNSET:
            field_dict["deep-lane-setting"] = deep_lane_setting
        if place_offset_pose is not UNSET:
            field_dict["place-offset-pose"] = place_offset_pose
        if load_jam_detection_enabled is not UNSET:
            field_dict["load-jam-detection-enabled"] = load_jam_detection_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bar import Bar
        from ..models.deep_lane_setting import DeepLaneSetting
        from ..models.elevation import Elevation
        from ..models.pose import Pose

        d = dict(src_dict)
        type_ = d.pop("type")

        map_id = UUID(d.pop("map-id"))

        name = d.pop("name")

        map_pose = Pose.from_dict(d.pop("map-pose"))

        utility_position_type = UtilityPositionType(d.pop("utility-position-type"))

        pallet_docking_option = PalletDockingOption(d.pop("pallet-docking-option"))

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

        _offset_pose = d.pop("offset-pose", UNSET)
        offset_pose: Pose | Unset
        if isinstance(_offset_pose, Unset):
            offset_pose = UNSET
        else:
            offset_pose = Pose.from_dict(_offset_pose)

        _bar = d.pop("bar", UNSET)
        bar: Bar | Unset
        if isinstance(_bar, Unset):
            bar = UNSET
        else:
            bar = Bar.from_dict(_bar)

        _elevation = d.pop("elevation", UNSET)
        elevation: Elevation | Unset
        if isinstance(_elevation, Unset):
            elevation = UNSET
        else:
            elevation = Elevation.from_dict(_elevation)

        _deep_lane_setting = d.pop("deep-lane-setting", UNSET)
        deep_lane_setting: DeepLaneSetting | Unset
        if isinstance(_deep_lane_setting, Unset):
            deep_lane_setting = UNSET
        else:
            deep_lane_setting = DeepLaneSetting.from_dict(_deep_lane_setting)

        _place_offset_pose = d.pop("place-offset-pose", UNSET)
        place_offset_pose: Pose | Unset
        if isinstance(_place_offset_pose, Unset):
            place_offset_pose = UNSET
        else:
            place_offset_pose = Pose.from_dict(_place_offset_pose)

        def _parse_load_jam_detection_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        load_jam_detection_enabled = _parse_load_jam_detection_enabled(
            d.pop("load-jam-detection-enabled", UNSET)
        )

        utility_position = cls(
            type_=type_,
            map_id=map_id,
            name=name,
            map_pose=map_pose,
            utility_position_type=utility_position_type,
            pallet_docking_option=pallet_docking_option,
            id=id,
            offset_pose=offset_pose,
            bar=bar,
            elevation=elevation,
            deep_lane_setting=deep_lane_setting,
            place_offset_pose=place_offset_pose,
            load_jam_detection_enabled=load_jam_detection_enabled,
        )

        utility_position.additional_properties = d
        return utility_position

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
