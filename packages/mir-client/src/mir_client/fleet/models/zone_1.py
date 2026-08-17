from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..models.zone_type import ZoneType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geo_json import GeoJson
    from ..models.zone_event import ZoneEvent


T = TypeVar("T", bound="Zone1")


@_attrs_define
class Zone1:
    """
    Attributes:
        name (str):
        map_id (UUID):
        geojson (GeoJson):
        type_ (ZoneType):
        id (None | Unset | UUID):
        events (list[ZoneEvent] | None | Unset):
    """

    name: str
    map_id: UUID
    geojson: GeoJson
    type_: ZoneType
    id: None | Unset | UUID = UNSET
    events: list[ZoneEvent] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        map_id = str(self.map_id)

        geojson = self.geojson.to_dict()

        type_ = self.type_.value

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        elif isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

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

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "map-id": map_id,
                "geojson": geojson,
                "type": type_,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if events is not UNSET:
            field_dict["events"] = events

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geo_json import GeoJson
        from ..models.zone_event import ZoneEvent

        d = dict(src_dict)
        name = d.pop("name")

        map_id = UUID(d.pop("map-id"))

        geojson = GeoJson.from_dict(d.pop("geojson"))

        type_ = ZoneType(d.pop("type"))

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

        zone_1 = cls(
            name=name,
            map_id=map_id,
            geojson=geojson,
            type_=type_,
            id=id,
            events=events,
        )

        return zone_1
