from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_robots_robots_item import PostRobotsRobotsItem


T = TypeVar("T", bound="PostRobots")


@_attrs_define
class PostRobots:
    """
    Attributes:
        robots (list[PostRobotsRobotsItem]):
        time (float):
    """

    robots: list[PostRobotsRobotsItem]
    time: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        robots = []
        for robots_item_data in self.robots:
            robots_item = robots_item_data.to_dict()
            robots.append(robots_item)

        time = self.time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "robots": robots,
                "time": time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_robots_robots_item import PostRobotsRobotsItem

        d = dict(src_dict)
        robots = []
        _robots = d.pop("robots")
        for robots_item_data in _robots:
            robots_item = PostRobotsRobotsItem.from_dict(robots_item_data)

            robots.append(robots_item)

        time = d.pop("time")

        post_robots = cls(
            robots=robots,
            time=time,
        )

        post_robots.additional_properties = d
        return post_robots

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
