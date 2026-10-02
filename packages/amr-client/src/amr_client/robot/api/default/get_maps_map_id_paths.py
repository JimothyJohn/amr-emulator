from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_map_paths import GetMapPaths
from ...types import Response


def _get_kwargs(
    map_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/maps/{map_id}/paths".format(
            map_id=quote(str(map_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | list[GetMapPaths] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetMapPaths.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 410:
        response_410 = Error.from_dict(response.json())

        return response_410

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | list[GetMapPaths]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    map_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[GetMapPaths]]:
    """
    Args:
        map_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[GetMapPaths]]
    """

    kwargs = _get_kwargs(
        map_id=map_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    map_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[GetMapPaths] | None:
    """
    Args:
        map_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[GetMapPaths]
    """

    return sync_detailed(
        map_id=map_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    map_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[GetMapPaths]]:
    """
    Args:
        map_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[GetMapPaths]]
    """

    kwargs = _get_kwargs(
        map_id=map_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    map_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[GetMapPaths] | None:
    """
    Args:
        map_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[GetMapPaths]
    """

    return (
        await asyncio_detailed(
            map_id=map_id,
            client=client,
        )
    ).parsed
