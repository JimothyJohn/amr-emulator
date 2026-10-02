from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_mission_queue_actions import GetMissionQueueActions
from ...types import Response


def _get_kwargs(
    mission_queue_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mission_queue/{mission_queue_id}/actions".format(
            mission_queue_id=quote(str(mission_queue_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetMissionQueueActions | None:
    if response.status_code == 200:
        response_200 = GetMissionQueueActions.from_dict(response.json())

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
) -> Response[Error | GetMissionQueueActions]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mission_queue_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | GetMissionQueueActions]:
    """
    Args:
        mission_queue_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetMissionQueueActions]
    """

    kwargs = _get_kwargs(
        mission_queue_id=mission_queue_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mission_queue_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetMissionQueueActions | None:
    """
    Args:
        mission_queue_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetMissionQueueActions
    """

    return sync_detailed(
        mission_queue_id=mission_queue_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    mission_queue_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | GetMissionQueueActions]:
    """
    Args:
        mission_queue_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetMissionQueueActions]
    """

    kwargs = _get_kwargs(
        mission_queue_id=mission_queue_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mission_queue_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetMissionQueueActions | None:
    """
    Args:
        mission_queue_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetMissionQueueActions
    """

    return (
        await asyncio_detailed(
            mission_queue_id=mission_queue_id,
            client=client,
        )
    ).parsed
