from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_position import BasePosition
from ...models.charger import Charger
from ...models.id_response import IdResponse
from ...models.marker import Marker
from ...models.problem_details import ProblemDetails
from ...models.utility_position import UtilityPosition
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BasePosition | Charger | Marker | Unset | UtilityPosition = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/site/position",
    }

    if isinstance(body, BasePosition):
        _kwargs["json"] = body.to_dict()
    elif isinstance(body, Charger):
        _kwargs["json"] = body.to_dict()
    elif isinstance(body, Marker):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    *,
    client: AuthenticatedClient | Client,
    body: BasePosition | Charger | Marker | Unset | UtilityPosition = UNSET,
) -> Response[IdResponse | ProblemDetails]:
    """Create a position or marker.

     Create a position of the following types: BasePosition, Charger, Marker, UtilityPosition.

    Args:
        body (BasePosition | Charger | Marker | Unset | UtilityPosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IdResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: BasePosition | Charger | Marker | Unset | UtilityPosition = UNSET,
) -> IdResponse | ProblemDetails | None:
    """Create a position or marker.

     Create a position of the following types: BasePosition, Charger, Marker, UtilityPosition.

    Args:
        body (BasePosition | Charger | Marker | Unset | UtilityPosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IdResponse | ProblemDetails
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: BasePosition | Charger | Marker | Unset | UtilityPosition = UNSET,
) -> Response[IdResponse | ProblemDetails]:
    """Create a position or marker.

     Create a position of the following types: BasePosition, Charger, Marker, UtilityPosition.

    Args:
        body (BasePosition | Charger | Marker | Unset | UtilityPosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IdResponse | ProblemDetails]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: BasePosition | Charger | Marker | Unset | UtilityPosition = UNSET,
) -> IdResponse | ProblemDetails | None:
    """Create a position or marker.

     Create a position of the following types: BasePosition, Charger, Marker, UtilityPosition.

    Args:
        body (BasePosition | Charger | Marker | Unset | UtilityPosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IdResponse | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
