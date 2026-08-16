from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSession")


@_attrs_define
class GetSession:
    """
    Attributes:
        active (bool | Unset): Boolean indicating whether the session is the active session in the fleet
        created_by (str | Unset): The url to the description of the type of this position
        created_by_id (str | Unset): The global id of the user who created this entry
        description (str | Unset): A possible description of the area
        export (str | Unset):
        guid (str | Unset): The global id unique across robots that identifies this area
        maps (str | Unset): The url to the list of maps that is in this area
        name (str | Unset): The name of the area
    """

    active: bool | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    description: str | Unset = UNSET
    export: str | Unset = UNSET
    guid: str | Unset = UNSET
    maps: str | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active = self.active

        created_by = self.created_by

        created_by_id = self.created_by_id

        description = self.description

        export = self.export

        guid = self.guid

        maps = self.maps

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active is not UNSET:
            field_dict["active"] = active
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if description is not UNSET:
            field_dict["description"] = description
        if export is not UNSET:
            field_dict["export"] = export
        if guid is not UNSET:
            field_dict["guid"] = guid
        if maps is not UNSET:
            field_dict["maps"] = maps
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        active = d.pop("active", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        description = d.pop("description", UNSET)

        export = d.pop("export", UNSET)

        guid = d.pop("guid", UNSET)

        maps = d.pop("maps", UNSET)

        name = d.pop("name", UNSET)

        get_session = cls(
            active=active,
            created_by=created_by,
            created_by_id=created_by_id,
            description=description,
            export=export,
            guid=guid,
            maps=maps,
            name=name,
        )

        get_session.additional_properties = d
        return get_session

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
