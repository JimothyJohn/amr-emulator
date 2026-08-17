from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostCert")


@_attrs_define
class PostCert:
    """
    Attributes:
        cert_key_file (str):
        cert_pem_file (str):
    """

    cert_key_file: str
    cert_pem_file: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cert_key_file = self.cert_key_file

        cert_pem_file = self.cert_pem_file

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cert_key_file": cert_key_file,
                "cert_pem_file": cert_pem_file,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cert_key_file = d.pop("cert_key_file")

        cert_pem_file = d.pop("cert_pem_file")

        post_cert = cls(
            cert_key_file=cert_key_file,
            cert_pem_file=cert_pem_file,
        )

        post_cert.additional_properties = d
        return post_cert

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
