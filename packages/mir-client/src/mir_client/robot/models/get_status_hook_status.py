from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_status_hook_status_cart import GetStatusHookStatusCart


T = TypeVar("T", bound="GetStatusHookStatus")


@_attrs_define
class GetStatusHookStatus:
    """
    Attributes:
        available (bool | Unset): Boolean indicating if the hook available on this robot
        cart (GetStatusHookStatusCart | Unset):
        cart_attached (bool | Unset): Boolean indicating if a trolley is currently attached
    """

    available: bool | Unset = UNSET
    cart: GetStatusHookStatusCart | Unset = UNSET
    cart_attached: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        available = self.available

        cart: dict[str, Any] | Unset = UNSET
        if not isinstance(self.cart, Unset):
            cart = self.cart.to_dict()

        cart_attached = self.cart_attached

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if available is not UNSET:
            field_dict["available"] = available
        if cart is not UNSET:
            field_dict["cart"] = cart
        if cart_attached is not UNSET:
            field_dict["cart_attached"] = cart_attached

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_status_hook_status_cart import GetStatusHookStatusCart

        d = dict(src_dict)
        available = d.pop("available", UNSET)

        _cart = d.pop("cart", UNSET)
        cart: GetStatusHookStatusCart | Unset
        if isinstance(_cart, Unset):
            cart = UNSET
        else:
            cart = GetStatusHookStatusCart.from_dict(_cart)

        cart_attached = d.pop("cart_attached", UNSET)

        get_status_hook_status = cls(
            available=available,
            cart=cart,
            cart_attached=cart_attached,
        )

        get_status_hook_status.additional_properties = d
        return get_status_hook_status

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
