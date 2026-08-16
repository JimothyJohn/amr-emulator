from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_contracts_response_contracts_item import EventContractsResponseContractsItem


T = TypeVar("T", bound="EventContractsResponse")


@_attrs_define
class EventContractsResponse:
    """
    Attributes:
        contracts (list[EventContractsResponseContractsItem] | Unset):
    """

    contracts: list[EventContractsResponseContractsItem] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        contracts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.contracts, Unset):
            contracts = []
            for contracts_item_data in self.contracts:
                contracts_item = contracts_item_data.to_dict()
                contracts.append(contracts_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if contracts is not UNSET:
            field_dict["contracts"] = contracts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_contracts_response_contracts_item import (
            EventContractsResponseContractsItem,
        )

        d = dict(src_dict)
        _contracts = d.pop("contracts", UNSET)
        contracts: list[EventContractsResponseContractsItem] | Unset = UNSET
        if _contracts is not UNSET:
            contracts = []
            for contracts_item_data in _contracts:
                contracts_item = EventContractsResponseContractsItem.from_dict(contracts_item_data)

                contracts.append(contracts_item)

        event_contracts_response = cls(
            contracts=contracts,
        )

        return event_contracts_response
