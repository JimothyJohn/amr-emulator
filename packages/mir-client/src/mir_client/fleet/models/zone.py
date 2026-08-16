from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.lock_zone_state import LockZoneState
from ..models.shape_type import ShapeType
from ..models.zone_type import ZoneType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.directional_zone import DirectionalZone
    from ..models.limit_zone import LimitZone
    from ..models.planner_zone import PlannerZone
    from ..models.point import Point
    from ..models.sound_and_light_zone import SoundAndLightZone
    from ..models.speed_zone import SpeedZone
    from ..models.zone_event import ZoneEvent


T = TypeVar("T", bound="Zone")


@_attrs_define
class Zone:
    """
    Attributes:
        type_ (ZoneType):
        name (str | Unset):
        map_id (str | Unset):
        polygon (list[Point] | Unset):
        events (list[ZoneEvent] | None | Unset):
        lock_zone_state (LockZoneState | Unset):
        stroke_width (float | None | Unset):
        shape_type (ShapeType | Unset):
        speed_zone (SpeedZone | Unset):
        sound_and_light_zone (SoundAndLightZone | Unset):
        planner_zone (PlannerZone | Unset):
        limit_zone (LimitZone | Unset):
        directional_zone (DirectionalZone | Unset):
    """

    type_: ZoneType
    name: str | Unset = UNSET
    map_id: str | Unset = UNSET
    polygon: list[Point] | Unset = UNSET
    events: list[ZoneEvent] | None | Unset = UNSET
    lock_zone_state: LockZoneState | Unset = UNSET
    stroke_width: float | None | Unset = UNSET
    shape_type: ShapeType | Unset = UNSET
    speed_zone: SpeedZone | Unset = UNSET
    sound_and_light_zone: SoundAndLightZone | Unset = UNSET
    planner_zone: PlannerZone | Unset = UNSET
    limit_zone: LimitZone | Unset = UNSET
    directional_zone: DirectionalZone | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        name = self.name

        map_id = self.map_id

        polygon: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.polygon, Unset):
            polygon = []
            for polygon_item_data in self.polygon:
                polygon_item = polygon_item_data.to_dict()
                polygon.append(polygon_item)

        events: list[dict[str, Any]] | None | Unset
        if isinstance(self.events, Unset):
            events = UNSET
        elif isinstance(self.events, list):
            events = []
            for events_type_0_item_data in self.events:
                events_type_0_item = events_type_0_item_data.to_dict()
                events.append(events_type_0_item)

        else:
            events = self.events

        lock_zone_state: str | Unset = UNSET
        if not isinstance(self.lock_zone_state, Unset):
            lock_zone_state = self.lock_zone_state.value

        stroke_width: float | None | Unset
        if isinstance(self.stroke_width, Unset):
            stroke_width = UNSET
        else:
            stroke_width = self.stroke_width

        shape_type: str | Unset = UNSET
        if not isinstance(self.shape_type, Unset):
            shape_type = self.shape_type.value

        speed_zone: dict[str, Any] | Unset = UNSET
        if not isinstance(self.speed_zone, Unset):
            speed_zone = self.speed_zone.to_dict()

        sound_and_light_zone: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sound_and_light_zone, Unset):
            sound_and_light_zone = self.sound_and_light_zone.to_dict()

        planner_zone: dict[str, Any] | Unset = UNSET
        if not isinstance(self.planner_zone, Unset):
            planner_zone = self.planner_zone.to_dict()

        limit_zone: dict[str, Any] | Unset = UNSET
        if not isinstance(self.limit_zone, Unset):
            limit_zone = self.limit_zone.to_dict()

        directional_zone: dict[str, Any] | Unset = UNSET
        if not isinstance(self.directional_zone, Unset):
            directional_zone = self.directional_zone.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if map_id is not UNSET:
            field_dict["map-id"] = map_id
        if polygon is not UNSET:
            field_dict["polygon"] = polygon
        if events is not UNSET:
            field_dict["events"] = events
        if lock_zone_state is not UNSET:
            field_dict["lock-zone-state"] = lock_zone_state
        if stroke_width is not UNSET:
            field_dict["stroke-width"] = stroke_width
        if shape_type is not UNSET:
            field_dict["shape-type"] = shape_type
        if speed_zone is not UNSET:
            field_dict["speed-zone"] = speed_zone
        if sound_and_light_zone is not UNSET:
            field_dict["sound-and-light-zone"] = sound_and_light_zone
        if planner_zone is not UNSET:
            field_dict["planner-zone"] = planner_zone
        if limit_zone is not UNSET:
            field_dict["limit-zone"] = limit_zone
        if directional_zone is not UNSET:
            field_dict["directional-zone"] = directional_zone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.directional_zone import DirectionalZone
        from ..models.limit_zone import LimitZone
        from ..models.planner_zone import PlannerZone
        from ..models.point import Point
        from ..models.sound_and_light_zone import SoundAndLightZone
        from ..models.speed_zone import SpeedZone
        from ..models.zone_event import ZoneEvent

        d = dict(src_dict)
        type_ = ZoneType(d.pop("type"))

        name = d.pop("name", UNSET)

        map_id = d.pop("map-id", UNSET)

        _polygon = d.pop("polygon", UNSET)
        polygon: list[Point] | Unset = UNSET
        if _polygon is not UNSET:
            polygon = []
            for polygon_item_data in _polygon:
                polygon_item = Point.from_dict(polygon_item_data)

                polygon.append(polygon_item)

        def _parse_events(data: object) -> list[ZoneEvent] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                events_type_0 = []
                _events_type_0 = data
                for events_type_0_item_data in _events_type_0:
                    events_type_0_item = ZoneEvent.from_dict(events_type_0_item_data)

                    events_type_0.append(events_type_0_item)

                return events_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ZoneEvent] | None | Unset, data)

        events = _parse_events(d.pop("events", UNSET))

        _lock_zone_state = d.pop("lock-zone-state", UNSET)
        lock_zone_state: LockZoneState | Unset
        if isinstance(_lock_zone_state, Unset):
            lock_zone_state = UNSET
        else:
            lock_zone_state = LockZoneState(_lock_zone_state)

        def _parse_stroke_width(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        stroke_width = _parse_stroke_width(d.pop("stroke-width", UNSET))

        _shape_type = d.pop("shape-type", UNSET)
        shape_type: ShapeType | Unset
        if isinstance(_shape_type, Unset):
            shape_type = UNSET
        else:
            shape_type = ShapeType(_shape_type)

        _speed_zone = d.pop("speed-zone", UNSET)
        speed_zone: SpeedZone | Unset
        if isinstance(_speed_zone, Unset):
            speed_zone = UNSET
        else:
            speed_zone = SpeedZone.from_dict(_speed_zone)

        _sound_and_light_zone = d.pop("sound-and-light-zone", UNSET)
        sound_and_light_zone: SoundAndLightZone | Unset
        if isinstance(_sound_and_light_zone, Unset):
            sound_and_light_zone = UNSET
        else:
            sound_and_light_zone = SoundAndLightZone.from_dict(_sound_and_light_zone)

        _planner_zone = d.pop("planner-zone", UNSET)
        planner_zone: PlannerZone | Unset
        if isinstance(_planner_zone, Unset):
            planner_zone = UNSET
        else:
            planner_zone = PlannerZone.from_dict(_planner_zone)

        _limit_zone = d.pop("limit-zone", UNSET)
        limit_zone: LimitZone | Unset
        if isinstance(_limit_zone, Unset):
            limit_zone = UNSET
        else:
            limit_zone = LimitZone.from_dict(_limit_zone)

        _directional_zone = d.pop("directional-zone", UNSET)
        directional_zone: DirectionalZone | Unset
        if isinstance(_directional_zone, Unset):
            directional_zone = UNSET
        else:
            directional_zone = DirectionalZone.from_dict(_directional_zone)

        zone = cls(
            type_=type_,
            name=name,
            map_id=map_id,
            polygon=polygon,
            events=events,
            lock_zone_state=lock_zone_state,
            stroke_width=stroke_width,
            shape_type=shape_type,
            speed_zone=speed_zone,
            sound_and_light_zone=sound_and_light_zone,
            planner_zone=planner_zone,
            limit_zone=limit_zone,
            directional_zone=directional_zone,
        )

        return zone
