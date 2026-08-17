from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..models.pallet_docking_option import PalletDockingOption
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bar import Bar
    from ..models.deep_lane_setting import DeepLaneSetting
    from ..models.elevation import Elevation
    from ..models.entry_position import EntryPosition
    from ..models.pose import Pose


T = TypeVar("T", bound="UpdatePositionRequest")


@_attrs_define
class UpdatePositionRequest:
    """
    Attributes:
        id (UUID):
        name (None | str | Unset):
        map_pose (Pose | Unset):
        offset_pose (Pose | Unset):
        bar (Bar | Unset):
        elevation (Elevation | Unset):
        entry_position_offset (Pose | Unset):
        entry_positions (list[EntryPosition] | None | Unset):
        deep_lane_setting (DeepLaneSetting | Unset):
        place_offset_pose (Pose | Unset):
        pallet_docking_option (PalletDockingOption | Unset):
        load_jam_detection_enabled (bool | None | Unset):
    """

    id: UUID
    name: None | str | Unset = UNSET
    map_pose: Pose | Unset = UNSET
    offset_pose: Pose | Unset = UNSET
    bar: Bar | Unset = UNSET
    elevation: Elevation | Unset = UNSET
    entry_position_offset: Pose | Unset = UNSET
    entry_positions: list[EntryPosition] | None | Unset = UNSET
    deep_lane_setting: DeepLaneSetting | Unset = UNSET
    place_offset_pose: Pose | Unset = UNSET
    pallet_docking_option: PalletDockingOption | Unset = UNSET
    load_jam_detection_enabled: bool | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        map_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.map_pose, Unset):
            map_pose = self.map_pose.to_dict()

        offset_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.offset_pose, Unset):
            offset_pose = self.offset_pose.to_dict()

        bar: dict[str, Any] | Unset = UNSET
        if not isinstance(self.bar, Unset):
            bar = self.bar.to_dict()

        elevation: dict[str, Any] | Unset = UNSET
        if not isinstance(self.elevation, Unset):
            elevation = self.elevation.to_dict()

        entry_position_offset: dict[str, Any] | Unset = UNSET
        if not isinstance(self.entry_position_offset, Unset):
            entry_position_offset = self.entry_position_offset.to_dict()

        entry_positions: list[dict[str, Any]] | None | Unset
        if isinstance(self.entry_positions, Unset):
            entry_positions = UNSET
        elif isinstance(self.entry_positions, list):
            entry_positions = []
            for entry_positions_type_0_item_data in self.entry_positions:
                entry_positions_type_0_item = entry_positions_type_0_item_data.to_dict()
                entry_positions.append(entry_positions_type_0_item)

        else:
            entry_positions = self.entry_positions

        deep_lane_setting: dict[str, Any] | Unset = UNSET
        if not isinstance(self.deep_lane_setting, Unset):
            deep_lane_setting = self.deep_lane_setting.to_dict()

        place_offset_pose: dict[str, Any] | Unset = UNSET
        if not isinstance(self.place_offset_pose, Unset):
            place_offset_pose = self.place_offset_pose.to_dict()

        pallet_docking_option: str | Unset = UNSET
        if not isinstance(self.pallet_docking_option, Unset):
            pallet_docking_option = self.pallet_docking_option.value

        load_jam_detection_enabled: bool | None | Unset
        if isinstance(self.load_jam_detection_enabled, Unset):
            load_jam_detection_enabled = UNSET
        else:
            load_jam_detection_enabled = self.load_jam_detection_enabled

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if map_pose is not UNSET:
            field_dict["map-pose"] = map_pose
        if offset_pose is not UNSET:
            field_dict["offset-pose"] = offset_pose
        if bar is not UNSET:
            field_dict["bar"] = bar
        if elevation is not UNSET:
            field_dict["elevation"] = elevation
        if entry_position_offset is not UNSET:
            field_dict["entry-position-offset"] = entry_position_offset
        if entry_positions is not UNSET:
            field_dict["entry-positions"] = entry_positions
        if deep_lane_setting is not UNSET:
            field_dict["deep-lane-setting"] = deep_lane_setting
        if place_offset_pose is not UNSET:
            field_dict["place-offset-pose"] = place_offset_pose
        if pallet_docking_option is not UNSET:
            field_dict["pallet-docking-option"] = pallet_docking_option
        if load_jam_detection_enabled is not UNSET:
            field_dict["load-jam-detection-enabled"] = load_jam_detection_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bar import Bar
        from ..models.deep_lane_setting import DeepLaneSetting
        from ..models.elevation import Elevation
        from ..models.entry_position import EntryPosition
        from ..models.pose import Pose

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        _map_pose = d.pop("map-pose", UNSET)
        map_pose: Pose | Unset
        if isinstance(_map_pose, Unset):
            map_pose = UNSET
        else:
            map_pose = Pose.from_dict(_map_pose)

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

        _entry_position_offset = d.pop("entry-position-offset", UNSET)
        entry_position_offset: Pose | Unset
        if isinstance(_entry_position_offset, Unset):
            entry_position_offset = UNSET
        else:
            entry_position_offset = Pose.from_dict(_entry_position_offset)

        def _parse_entry_positions(data: object) -> list[EntryPosition] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                entry_positions_type_0 = []
                _entry_positions_type_0 = data
                for entry_positions_type_0_item_data in _entry_positions_type_0:
                    entry_positions_type_0_item = EntryPosition.from_dict(
                        entry_positions_type_0_item_data
                    )

                    entry_positions_type_0.append(entry_positions_type_0_item)

                return entry_positions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[EntryPosition] | None | Unset, data)

        entry_positions = _parse_entry_positions(d.pop("entry-positions", UNSET))

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

        _pallet_docking_option = d.pop("pallet-docking-option", UNSET)
        pallet_docking_option: PalletDockingOption | Unset
        if isinstance(_pallet_docking_option, Unset):
            pallet_docking_option = UNSET
        else:
            pallet_docking_option = PalletDockingOption(_pallet_docking_option)

        def _parse_load_jam_detection_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        load_jam_detection_enabled = _parse_load_jam_detection_enabled(
            d.pop("load-jam-detection-enabled", UNSET)
        )

        update_position_request = cls(
            id=id,
            name=name,
            map_pose=map_pose,
            offset_pose=offset_pose,
            bar=bar,
            elevation=elevation,
            entry_position_offset=entry_position_offset,
            entry_positions=entry_positions,
            deep_lane_setting=deep_lane_setting,
            place_offset_pose=place_offset_pose,
            pallet_docking_option=pallet_docking_option,
            load_jam_detection_enabled=load_jam_detection_enabled,
        )

        return update_position_request
