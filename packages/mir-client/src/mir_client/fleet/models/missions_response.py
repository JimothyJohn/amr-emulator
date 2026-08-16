from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.guid_and_name import GuidAndName


T = TypeVar("T", bound="MissionsResponse")


@_attrs_define
class MissionsResponse:
    """
    Attributes:
        missions (list[GuidAndName]):
    """

    missions: list[GuidAndName]

    def to_dict(self) -> dict[str, Any]:
        missions = []
        for missions_item_data in self.missions:
            missions_item = missions_item_data.to_dict()
            missions.append(missions_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "missions": missions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.guid_and_name import GuidAndName

        d = dict(src_dict)
        missions = []
        _missions = d.pop("missions")
        for missions_item_data in _missions:
            missions_item = GuidAndName.from_dict(missions_item_data)

            missions.append(missions_item)

        missions_response = cls(
            missions=missions,
        )

        return missions_response
