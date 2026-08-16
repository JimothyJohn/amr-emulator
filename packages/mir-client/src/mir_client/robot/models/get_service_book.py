from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetServiceBook")


@_attrs_define
class GetServiceBook:
    """
    Attributes:
        created_at (str | Unset): Creation time of the service note
        created_by (str | Unset): The url to the user
        created_by_id (str | Unset): The user which created the log
        created_by_name (str | Unset): The user name which created the log
        description (str | Unset): The sevice note
        guid (str | Unset): The global unique id across robots that identifies this service note
        owner_group (str | Unset): The url to the owner group
        owner_group_guid (str | Unset): The usergroup which owns the service book
        owner_group_name (str | Unset): The group name which owns the log
    """

    created_at: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created_by_id: str | Unset = UNSET
    created_by_name: str | Unset = UNSET
    description: str | Unset = UNSET
    guid: str | Unset = UNSET
    owner_group: str | Unset = UNSET
    owner_group_guid: str | Unset = UNSET
    owner_group_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at

        created_by = self.created_by

        created_by_id = self.created_by_id

        created_by_name = self.created_by_name

        description = self.description

        guid = self.guid

        owner_group = self.owner_group

        owner_group_guid = self.owner_group_guid

        owner_group_name = self.owner_group_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if created_by_name is not UNSET:
            field_dict["created_by_name"] = created_by_name
        if description is not UNSET:
            field_dict["description"] = description
        if guid is not UNSET:
            field_dict["guid"] = guid
        if owner_group is not UNSET:
            field_dict["owner_group"] = owner_group
        if owner_group_guid is not UNSET:
            field_dict["owner_group_guid"] = owner_group_guid
        if owner_group_name is not UNSET:
            field_dict["owner_group_name"] = owner_group_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = d.pop("created_at", UNSET)

        created_by = d.pop("created_by", UNSET)

        created_by_id = d.pop("created_by_id", UNSET)

        created_by_name = d.pop("created_by_name", UNSET)

        description = d.pop("description", UNSET)

        guid = d.pop("guid", UNSET)

        owner_group = d.pop("owner_group", UNSET)

        owner_group_guid = d.pop("owner_group_guid", UNSET)

        owner_group_name = d.pop("owner_group_name", UNSET)

        get_service_book = cls(
            created_at=created_at,
            created_by=created_by,
            created_by_id=created_by_id,
            created_by_name=created_by_name,
            description=description,
            guid=guid,
            owner_group=owner_group,
            owner_group_guid=owner_group_guid,
            owner_group_name=owner_group_name,
        )

        get_service_book.additional_properties = d
        return get_service_book

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
