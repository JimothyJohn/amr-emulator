from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pallet_docking_option import PalletDockingOption
from ..models.utility_position_type import UtilityPositionType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bar_1 import Bar1
    from ..models.deep_lane_setting_1 import DeepLaneSetting1
    from ..models.elevation_1 import Elevation1
    from ..models.entry_position_1 import EntryPosition1
    from ..models.pose_1 import Pose1


T = TypeVar("T", bound="UtilityPosition1")


@_attrs_define
class UtilityPosition1:
    """
    Attributes:
        type_ (UtilityPositionType):
        pallet_docking_option (PalletDockingOption):
        load_jam_detection_enabled (bool):
        map_id (str | Unset):
        name (str | Unset):
        map_pose (Pose1 | Unset):
        entry_positions (list[EntryPosition1] | Unset):
        offset_pose (Pose1 | Unset):
        bar (Bar1 | Unset):
        elevation (Elevation1 | Unset):
        deep_lane_setting (DeepLaneSetting1 | Unset):
        place_offset_pose (Pose1 | Unset):
    """

    type_: UtilityPositionType
    pallet_docking_option: PalletDockingOption
    load_jam_detection_enabled: bool
    map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    map_pose: Pose1 | Unset = UNSET
    entry_positions: list[EntryPosition1] | Unset = UNSET
    offset_pose: Pose1 | Unset = UNSET
    bar: Bar1 | Unset = UNSET
    elevation: Elevation1 | Unset = UNSET
    deep_lane_setting: DeepLaneSetting1 | Unset = UNSET
    place_offset_pose: Pose1 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        pallet_docking_option = self.pallet_docking_option.value

        load_jam_detection_enabled = self.load_jam_detection_enabled

        map_id = self.map_id

        name = self.name

        map_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.map_pose, Unset):
            map_pose = self.map_pose.to_dict()

        entry_positions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.entry_positions, Unset):
            entry_positions = []
            for entry_positions_item_data in self.entry_positions:
                entry_positions_item = entry_positions_item_data.to_dict()
                entry_positions.append(entry_positions_item)

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "pallet-docking-option": pallet_docking_option,
                "load-jam-detection-enabled": load_jam_detection_enabled,
            }
        )
        if map_id is not UNSET:
            field_dict["map-id"] = map_id
        if name is not UNSET:
            field_dict["name"] = name
        if map_pose is not UNSET:
            field_dict["map-pose"] = map_pose
        if entry_positions is not UNSET:
            field_dict["entry-positions"] = entry_positions
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bar_1 import Bar1
        from ..models.deep_lane_setting_1 import DeepLaneSetting1
        from ..models.elevation_1 import Elevation1
        from ..models.entry_position_1 import EntryPosition1
        from ..models.pose_1 import Pose1

        d = dict(src_dict)
        type_ = UtilityPositionType(d.pop("type"))

        pallet_docking_option = PalletDockingOption(d.pop("pallet-docking-option"))

        load_jam_detection_enabled = d.pop("load-jam-detection-enabled")

        map_id = d.pop("map-id", UNSET)

        name = d.pop("name", UNSET)

        _map_pose = d.pop("map-pose", UNSET)
        map_pose: Pose1 | Unset
        if isinstance(_map_pose, Unset):
            map_pose = UNSET
        else:
            map_pose = Pose1.from_dict(_map_pose)

        _entry_positions = d.pop("entry-positions", UNSET)
        entry_positions: list[EntryPosition1] | Unset = UNSET
        if _entry_positions is not UNSET:
            entry_positions = []
            for entry_positions_item_data in _entry_positions:
                entry_positions_item = EntryPosition1.from_dict(entry_positions_item_data)

                entry_positions.append(entry_positions_item)

        _offset_pose = d.pop("offset-pose", UNSET)
        offset_pose: Pose1 | Unset
        if isinstance(_offset_pose, Unset):
            offset_pose = UNSET
        else:
            offset_pose = Pose1.from_dict(_offset_pose)

        _bar = d.pop("bar", UNSET)
        bar: Bar1 | Unset
        if isinstance(_bar, Unset):
            bar = UNSET
        else:
            bar = Bar1.from_dict(_bar)

        _elevation = d.pop("elevation", UNSET)
        elevation: Elevation1 | Unset
        if isinstance(_elevation, Unset):
            elevation = UNSET
        else:
            elevation = Elevation1.from_dict(_elevation)

        _deep_lane_setting = d.pop("deep-lane-setting", UNSET)
        deep_lane_setting: DeepLaneSetting1 | Unset
        if isinstance(_deep_lane_setting, Unset):
            deep_lane_setting = UNSET
        else:
            deep_lane_setting = DeepLaneSetting1.from_dict(_deep_lane_setting)

        _place_offset_pose = d.pop("place-offset-pose", UNSET)
        place_offset_pose: Pose1 | Unset
        if isinstance(_place_offset_pose, Unset):
            place_offset_pose = UNSET
        else:
            place_offset_pose = Pose1.from_dict(_place_offset_pose)

        utility_position_1 = cls(
            type_=type_,
            pallet_docking_option=pallet_docking_option,
            load_jam_detection_enabled=load_jam_detection_enabled,
            map_id=map_id,
            name=name,
            map_pose=map_pose,
            entry_positions=entry_positions,
            offset_pose=offset_pose,
            bar=bar,
            elevation=elevation,
            deep_lane_setting=deep_lane_setting,
            place_offset_pose=place_offset_pose,
        )

        utility_position_1.additional_properties = d
        return utility_position_1

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
