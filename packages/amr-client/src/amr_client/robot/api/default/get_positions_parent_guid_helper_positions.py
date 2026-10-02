from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_helper_positions import GetHelperPositions
from ...types import Response


def _get_kwargs(
    parent_guid: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/positions/{parent_guid}/helper_positions".format(
            parent_guid=quote(str(parent_guid), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | list[GetHelperPositions] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetHelperPositions.from_dict(response_200_item_data)

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
) -> Response[Error | list[GetHelperPositions]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    parent_guid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[GetHelperPositions]]:
    """
    Args:
        parent_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[GetHelperPositions]]
    """

    kwargs = _get_kwargs(
        parent_guid=parent_guid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    parent_guid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[GetHelperPositions] | None:
    """
    Args:
        parent_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[GetHelperPositions]
    """

    return sync_detailed(
        parent_guid=parent_guid,
        client=client,
    ).parsed


async def asyncio_detailed(
    parent_guid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[GetHelperPositions]]:
    """
    Args:
        parent_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[GetHelperPositions]]
    """

    kwargs = _get_kwargs(
        parent_guid=parent_guid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    parent_guid: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[GetHelperPositions] | None:
    """
    Args:
        parent_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[GetHelperPositions]
    """

    return (
        await asyncio_detailed(
            parent_guid=parent_guid,
            client=client,
        )
    ).parsed
