from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_action_definition import GetActionDefinition
from ...types import Response


def _get_kwargs(
    action_type: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/actions/{action_type}".format(
            action_type=quote(str(action_type), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetActionDefinition | None:
    if response.status_code == 200:
        response_200 = GetActionDefinition.from_dict(response.json())

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
) -> Response[Error | GetActionDefinition]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    action_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | GetActionDefinition]:
    """
    Args:
        action_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetActionDefinition]
    """

    kwargs = _get_kwargs(
        action_type=action_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    action_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetActionDefinition | None:
    """
    Args:
        action_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetActionDefinition
    """

    return sync_detailed(
        action_type=action_type,
        client=client,
    ).parsed


async def asyncio_detailed(
    action_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | GetActionDefinition]:
    """
    Args:
        action_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetActionDefinition]
    """

    kwargs = _get_kwargs(
        action_type=action_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    action_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetActionDefinition | None:
    """
    Args:
        action_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetActionDefinition
    """

    return (
        await asyncio_detailed(
            action_type=action_type,
            client=client,
        )
    ).parsed
