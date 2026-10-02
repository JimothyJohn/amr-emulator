from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.id_response import IdResponse
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    serial_order_id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/serial-order/fallback/{serial_order_id}".format(
            serial_order_id=quote(str(serial_order_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> IdResponse | ProblemDetails | None:
    if response.status_code == 202:
        response_202 = IdResponse.from_dict(response.json())

        return response_202

    if response.status_code == 400:
        response_400 = ProblemDetails.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = ProblemDetails.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[IdResponse | ProblemDetails]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    serial_order_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[IdResponse | ProblemDetails]:
    """Abort a fallback

     Abort a specific serial order's fallback mission by specifying its id in the endpoint.

    Args:
        serial_order_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IdResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        serial_order_id=serial_order_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    serial_order_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> IdResponse | ProblemDetails | None:
    """Abort a fallback

     Abort a specific serial order's fallback mission by specifying its id in the endpoint.

    Args:
        serial_order_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IdResponse | ProblemDetails
    """

    return sync_detailed(
        serial_order_id=serial_order_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    serial_order_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[IdResponse | ProblemDetails]:
    """Abort a fallback

     Abort a specific serial order's fallback mission by specifying its id in the endpoint.

    Args:
        serial_order_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IdResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        serial_order_id=serial_order_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    serial_order_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> IdResponse | ProblemDetails | None:
    """Abort a fallback

     Abort a specific serial order's fallback mission by specifying its id in the endpoint.

    Args:
        serial_order_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IdResponse | ProblemDetails
    """

    return (
        await asyncio_detailed(
            serial_order_id=serial_order_id,
            client=client,
        )
    ).parsed
