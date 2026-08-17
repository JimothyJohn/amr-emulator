from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_world_model_world_model_item import PostWorldModelWorldModelItem


T = TypeVar("T", bound="PostWorldModel")


@_attrs_define
class PostWorldModel:
    """
    Attributes:
        enable_resource_tracking (bool):
        robot_ip (str):
        world_model (list[PostWorldModelWorldModelItem]):
        fleet_id (str | Unset):
    """

    enable_resource_tracking: bool
    robot_ip: str
    world_model: list[PostWorldModelWorldModelItem]
    fleet_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable_resource_tracking = self.enable_resource_tracking

        robot_ip = self.robot_ip

        world_model = []
        for world_model_item_data in self.world_model:
            world_model_item = world_model_item_data.to_dict()
            world_model.append(world_model_item)

        fleet_id = self.fleet_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enable_resource_tracking": enable_resource_tracking,
                "robot_ip": robot_ip,
                "world_model": world_model,
            }
        )
        if fleet_id is not UNSET:
            field_dict["fleet_id"] = fleet_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_world_model_world_model_item import PostWorldModelWorldModelItem

        d = dict(src_dict)
        enable_resource_tracking = d.pop("enable_resource_tracking")

        robot_ip = d.pop("robot_ip")

        world_model = []
        _world_model = d.pop("world_model")
        for world_model_item_data in _world_model:
            world_model_item = PostWorldModelWorldModelItem.from_dict(world_model_item_data)

            world_model.append(world_model_item)

        fleet_id = d.pop("fleet_id", UNSET)

        post_world_model = cls(
            enable_resource_tracking=enable_resource_tracking,
            robot_ip=robot_ip,
            world_model=world_model,
            fleet_id=fleet_id,
        )

        post_world_model.additional_properties = d
        return post_world_model

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
