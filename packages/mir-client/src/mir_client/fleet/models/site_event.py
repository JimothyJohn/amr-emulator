from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.site_action_type import SiteActionType
from ..models.site_entity_type import SiteEntityType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cart import Cart
    from ..models.footprint_1 import Footprint1
    from ..models.io_module import IoModule
    from ..models.map_1 import Map1
    from ..models.marker_type import MarkerType
    from ..models.mission import Mission
    from ..models.position_1 import Position1
    from ..models.sound import Sound
    from ..models.zone import Zone


T = TypeVar("T", bound="SiteEvent")


@_attrs_define
class SiteEvent:
    """
    Attributes:
        entity_id (str):
        entity_type (SiteEntityType):
        action_type (SiteActionType):
        status_change_timestamp (datetime.datetime | Unset):
        map_ (Map1 | Unset):
        position (Position1 | Unset):
        zone (Zone | Unset):
        mission (Mission | Unset):
        cart (Cart | Unset):
        marker_type (MarkerType | Unset):
        footprint (Footprint1 | Unset):
        io_module (IoModule | Unset):
        sound (Sound | Unset):
    """

    entity_id: str
    entity_type: SiteEntityType
    action_type: SiteActionType
    status_change_timestamp: datetime.datetime | Unset = UNSET
    map_: Map1 | Unset = UNSET
    position: Position1 | Unset = UNSET
    zone: Zone | Unset = UNSET
    mission: Mission | Unset = UNSET
    cart: Cart | Unset = UNSET
    marker_type: MarkerType | Unset = UNSET
    footprint: Footprint1 | Unset = UNSET
    io_module: IoModule | Unset = UNSET
    sound: Sound | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        entity_id = self.entity_id

        entity_type = self.entity_type.value

        action_type = self.action_type.value

        status_change_timestamp: str | Unset = UNSET
        if not isinstance(self.status_change_timestamp, Unset):
            status_change_timestamp = self.status_change_timestamp.isoformat()

        map_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.map_, Unset):
            map_ = self.map_.to_dict()

        position: dict[str, Any] | Unset = UNSET
        if not isinstance(self.position, Unset):
            position = self.position.to_dict()

        zone: dict[str, Any] | Unset = UNSET
        if not isinstance(self.zone, Unset):
            zone = self.zone.to_dict()

        mission: dict[str, Any] | Unset = UNSET
        if not isinstance(self.mission, Unset):
            mission = self.mission.to_dict()

        cart: dict[str, Any] | Unset = UNSET
        if not isinstance(self.cart, Unset):
            cart = self.cart.to_dict()

        marker_type: dict[str, Any] | Unset = UNSET
        if not isinstance(self.marker_type, Unset):
            marker_type = self.marker_type.to_dict()

        footprint: dict[str, Any] | Unset = UNSET
        if not isinstance(self.footprint, Unset):
            footprint = self.footprint.to_dict()

        io_module: dict[str, Any] | Unset = UNSET
        if not isinstance(self.io_module, Unset):
            io_module = self.io_module.to_dict()

        sound: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sound, Unset):
            sound = self.sound.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "entity-id": entity_id,
                "entity-type": entity_type,
                "action-type": action_type,
            }
        )
        if status_change_timestamp is not UNSET:
            field_dict["status-change-timestamp"] = status_change_timestamp
        if map_ is not UNSET:
            field_dict["map"] = map_
        if position is not UNSET:
            field_dict["position"] = position
        if zone is not UNSET:
            field_dict["zone"] = zone
        if mission is not UNSET:
            field_dict["mission"] = mission
        if cart is not UNSET:
            field_dict["cart"] = cart
        if marker_type is not UNSET:
            field_dict["marker-type"] = marker_type
        if footprint is not UNSET:
            field_dict["footprint"] = footprint
        if io_module is not UNSET:
            field_dict["io-module"] = io_module
        if sound is not UNSET:
            field_dict["sound"] = sound

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cart import Cart
        from ..models.footprint_1 import Footprint1
        from ..models.io_module import IoModule
        from ..models.map_1 import Map1
        from ..models.marker_type import MarkerType
        from ..models.mission import Mission
        from ..models.position_1 import Position1
        from ..models.sound import Sound
        from ..models.zone import Zone

        d = dict(src_dict)
        entity_id = d.pop("entity-id")

        entity_type = SiteEntityType(d.pop("entity-type"))

        action_type = SiteActionType(d.pop("action-type"))

        _status_change_timestamp = d.pop("status-change-timestamp", UNSET)
        status_change_timestamp: datetime.datetime | Unset
        if isinstance(_status_change_timestamp, Unset):
            status_change_timestamp = UNSET
        else:
            status_change_timestamp = datetime.datetime.fromisoformat(_status_change_timestamp)

        _map_ = d.pop("map", UNSET)
        map_: Map1 | Unset
        if isinstance(_map_, Unset):
            map_ = UNSET
        else:
            map_ = Map1.from_dict(_map_)

        _position = d.pop("position", UNSET)
        position: Position1 | Unset
        if isinstance(_position, Unset):
            position = UNSET
        else:
            position = Position1.from_dict(_position)

        _zone = d.pop("zone", UNSET)
        zone: Zone | Unset
        if isinstance(_zone, Unset):
            zone = UNSET
        else:
            zone = Zone.from_dict(_zone)

        _mission = d.pop("mission", UNSET)
        mission: Mission | Unset
        if isinstance(_mission, Unset):
            mission = UNSET
        else:
            mission = Mission.from_dict(_mission)

        _cart = d.pop("cart", UNSET)
        cart: Cart | Unset
        if isinstance(_cart, Unset):
            cart = UNSET
        else:
            cart = Cart.from_dict(_cart)

        _marker_type = d.pop("marker-type", UNSET)
        marker_type: MarkerType | Unset
        if isinstance(_marker_type, Unset):
            marker_type = UNSET
        else:
            marker_type = MarkerType.from_dict(_marker_type)

        _footprint = d.pop("footprint", UNSET)
        footprint: Footprint1 | Unset
        if isinstance(_footprint, Unset):
            footprint = UNSET
        else:
            footprint = Footprint1.from_dict(_footprint)

        _io_module = d.pop("io-module", UNSET)
        io_module: IoModule | Unset
        if isinstance(_io_module, Unset):
            io_module = UNSET
        else:
            io_module = IoModule.from_dict(_io_module)

        _sound = d.pop("sound", UNSET)
        sound: Sound | Unset
        if isinstance(_sound, Unset):
            sound = UNSET
        else:
            sound = Sound.from_dict(_sound)

        site_event = cls(
            entity_id=entity_id,
            entity_type=entity_type,
            action_type=action_type,
            status_change_timestamp=status_change_timestamp,
            map_=map_,
            position=position,
            zone=zone,
            mission=mission,
            cart=cart,
            marker_type=marker_type,
            footprint=footprint,
            io_module=io_module,
            sound=sound,
        )

        return site_event
