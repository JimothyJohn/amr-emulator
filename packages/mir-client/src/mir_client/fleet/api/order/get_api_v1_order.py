import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.order_status_1 import OrderStatus1
from ...models.problem_details import ProblemDetails
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    order_statuses: list[OrderStatus1] | Unset = UNSET,
    created_after: datetime.datetime | Unset = UNSET,
    terminated_after: datetime.datetime | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_order_statuses: list[str] | Unset = UNSET
    if not isinstance(order_statuses, Unset):
        json_order_statuses = []
        for order_statuses_item_data in order_statuses:
            order_statuses_item = order_statuses_item_data.value
            json_order_statuses.append(order_statuses_item)

    params["orderStatuses"] = json_order_statuses

    json_created_after: str | Unset = UNSET
    if not isinstance(created_after, Unset):
        json_created_after = created_after.isoformat()
    params["createdAfter"] = json_created_after

    json_terminated_after: str | Unset = UNSET
    if not isinstance(terminated_after, Unset):
        json_terminated_after = terminated_after.isoformat()
    params["terminatedAfter"] = json_terminated_after

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/order",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ProblemDetails | list[Any] | None:
    if response.status_code == 200:
        response_200 = cast(list[Any], response.json())

        return response_200

    if response.status_code == 500:
        response_500 = ProblemDetails.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ProblemDetails | list[Any]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    order_statuses: list[OrderStatus1] | Unset = UNSET,
    created_after: datetime.datetime | Unset = UNSET,
    terminated_after: datetime.datetime | Unset = UNSET,
) -> Response[ProblemDetails | list[Any]]:
    """Get orders (supports JSON or CSV)

     Get log of executing or terminated orders. By default, orders terminated in the last hour are
    included.
    Use the Accept header to request types text/csv or application/json.

    Args:
        order_statuses (list[OrderStatus1] | Unset):
        created_after (datetime.datetime | Unset):
        terminated_after (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProblemDetails | list[Any]]
    """

    kwargs = _get_kwargs(
        order_statuses=order_statuses,
        created_after=created_after,
        terminated_after=terminated_after,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    order_statuses: list[OrderStatus1] | Unset = UNSET,
    created_after: datetime.datetime | Unset = UNSET,
    terminated_after: datetime.datetime | Unset = UNSET,
) -> ProblemDetails | list[Any] | None:
    """Get orders (supports JSON or CSV)

     Get log of executing or terminated orders. By default, orders terminated in the last hour are
    included.
    Use the Accept header to request types text/csv or application/json.

    Args:
        order_statuses (list[OrderStatus1] | Unset):
        created_after (datetime.datetime | Unset):
        terminated_after (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProblemDetails | list[Any]
    """

    return sync_detailed(
        client=client,
        order_statuses=order_statuses,
        created_after=created_after,
        terminated_after=terminated_after,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    order_statuses: list[OrderStatus1] | Unset = UNSET,
    created_after: datetime.datetime | Unset = UNSET,
    terminated_after: datetime.datetime | Unset = UNSET,
) -> Response[ProblemDetails | list[Any]]:
    """Get orders (supports JSON or CSV)

     Get log of executing or terminated orders. By default, orders terminated in the last hour are
    included.
    Use the Accept header to request types text/csv or application/json.

    Args:
        order_statuses (list[OrderStatus1] | Unset):
        created_after (datetime.datetime | Unset):
        terminated_after (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProblemDetails | list[Any]]
    """

    kwargs = _get_kwargs(
        order_statuses=order_statuses,
        created_after=created_after,
        terminated_after=terminated_after,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    order_statuses: list[OrderStatus1] | Unset = UNSET,
    created_after: datetime.datetime | Unset = UNSET,
    terminated_after: datetime.datetime | Unset = UNSET,
) -> ProblemDetails | list[Any] | None:
    """Get orders (supports JSON or CSV)

     Get log of executing or terminated orders. By default, orders terminated in the last hour are
    included.
    Use the Accept header to request types text/csv or application/json.

    Args:
        order_statuses (list[OrderStatus1] | Unset):
        created_after (datetime.datetime | Unset):
        terminated_after (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProblemDetails | list[Any]
    """

    return (
        await asyncio_detailed(
            client=client,
            order_statuses=order_statuses,
            created_after=created_after,
            terminated_after=terminated_after,
        )
    ).parsed
