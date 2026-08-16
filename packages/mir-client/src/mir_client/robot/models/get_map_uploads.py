from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMapUploads")


@_attrs_define
class GetMapUploads:
    """
    Attributes:
        guid (str | Unset): The global guid of this map upload
        state (str | Unset):
        type_ (str | Unset):
        url (str | Unset): The URL of the resource
    """

    guid: str | Unset = UNSET
    state: str | Unset = UNSET
    type_: str | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guid = self.guid

        state = self.state

        type_ = self.type_

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guid is not UNSET:
            field_dict["guid"] = guid
        if state is not UNSET:
            field_dict["state"] = state
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guid = d.pop("guid", UNSET)

        state = d.pop("state", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        get_map_uploads = cls(
            guid=guid,
            state=state,
            type_=type_,
            url=url,
        )

        get_map_uploads.additional_properties = d
        return get_map_uploads

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
