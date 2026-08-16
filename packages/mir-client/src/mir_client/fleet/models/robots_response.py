from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.robot_identity import RobotIdentity


T = TypeVar("T", bound="RobotsResponse")


@_attrs_define
class RobotsResponse:
    """
    Attributes:
        robots (list[RobotIdentity]):
    """

    robots: list[RobotIdentity]

    def to_dict(self) -> dict[str, Any]:
        robots = []
        for robots_item_data in self.robots:
            robots_item = robots_item_data.to_dict()
            robots.append(robots_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "robots": robots,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.robot_identity import RobotIdentity

        d = dict(src_dict)
        robots = []
        _robots = d.pop("robots")
        for robots_item_data in _robots:
            robots_item = RobotIdentity.from_dict(robots_item_data)

            robots.append(robots_item)

        robots_response = cls(
            robots=robots,
        )

        return robots_response
