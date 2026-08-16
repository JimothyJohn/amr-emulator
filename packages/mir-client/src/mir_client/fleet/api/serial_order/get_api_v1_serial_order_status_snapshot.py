from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_details import ProblemDetails
from ...models.serial_order_status_snapshot_response import SerialOrderStatusSnapshotResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/serial-order-status/snapshot",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ProblemDetails | SerialOrderStatusSnapshotResponse | None:
    if response.status_code == 200:
        response_200 = SerialOrderStatusSnapshotResponse.from_dict(response.json())

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
) -> Response[ProblemDetails | SerialOrderStatusSnapshotResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ProblemDetails | SerialOrderStatusSnapshotResponse]:
    """Get serial order status snapshot

     Get a list of all active orders in MiR Fleet. This includes scheduled order and orders currently
    being executed.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProblemDetails | SerialOrderStatusSnapshotResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> ProblemDetails | SerialOrderStatusSnapshotResponse | None:
    """Get serial order status snapshot

     Get a list of all active orders in MiR Fleet. This includes scheduled order and orders currently
    being executed.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProblemDetails | SerialOrderStatusSnapshotResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ProblemDetails | SerialOrderStatusSnapshotResponse]:
    """Get serial order status snapshot

     Get a list of all active orders in MiR Fleet. This includes scheduled order and orders currently
    being executed.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProblemDetails | SerialOrderStatusSnapshotResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> ProblemDetails | SerialOrderStatusSnapshotResponse | None:
    """Get serial order status snapshot

     Get a list of all active orders in MiR Fleet. This includes scheduled order and orders currently
    being executed.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProblemDetails | SerialOrderStatusSnapshotResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
