from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_group_action_definition import GetGroupActionDefinition
from ...types import Response


def _get_kwargs(
    mission_group_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mission_groups/{mission_group_id}/actions".format(
            mission_group_id=quote(str(mission_group_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetGroupActionDefinition | None:
    if response.status_code == 200:
        response_200 = GetGroupActionDefinition.from_dict(response.json())

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
) -> Response[Error | GetGroupActionDefinition]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mission_group_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | GetGroupActionDefinition]:
    """
    Args:
        mission_group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetGroupActionDefinition]
    """

    kwargs = _get_kwargs(
        mission_group_id=mission_group_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mission_group_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetGroupActionDefinition | None:
    """
    Args:
        mission_group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetGroupActionDefinition
    """

    return sync_detailed(
        mission_group_id=mission_group_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    mission_group_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | GetGroupActionDefinition]:
    """
    Args:
        mission_group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetGroupActionDefinition]
    """

    kwargs = _get_kwargs(
        mission_group_id=mission_group_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mission_group_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetGroupActionDefinition | None:
    """
    Args:
        mission_group_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetGroupActionDefinition
    """

    return (
        await asyncio_detailed(
            mission_group_id=mission_group_id,
            client=client,
        )
    ).parsed
