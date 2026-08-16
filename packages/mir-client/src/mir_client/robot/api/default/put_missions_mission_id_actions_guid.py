from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_mission_action import GetMissionAction
from ...models.put_mission_action import PutMissionAction
from ...types import Response


def _get_kwargs(
    mission_id: str,
    guid: str,
    *,
    body: PutMissionAction,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/missions/{mission_id}/actions/{guid}".format(
            mission_id=quote(str(mission_id), safe=""),
            guid=quote(str(guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetMissionAction | None:
    if response.status_code == 200:
        response_200 = GetMissionAction.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | GetMissionAction]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mission_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutMissionAction,
) -> Response[Error | GetMissionAction]:
    """
    Args:
        mission_id (str):
        guid (str):
        body (PutMissionAction):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetMissionAction]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        guid=guid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mission_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutMissionAction,
) -> Error | GetMissionAction | None:
    """
    Args:
        mission_id (str):
        guid (str):
        body (PutMissionAction):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetMissionAction
    """

    return sync_detailed(
        mission_id=mission_id,
        guid=guid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    mission_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutMissionAction,
) -> Response[Error | GetMissionAction]:
    """
    Args:
        mission_id (str):
        guid (str):
        body (PutMissionAction):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetMissionAction]
    """

    kwargs = _get_kwargs(
        mission_id=mission_id,
        guid=guid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mission_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutMissionAction,
) -> Error | GetMissionAction | None:
    """
    Args:
        mission_id (str):
        guid (str):
        body (PutMissionAction):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetMissionAction
    """

    return (
        await asyncio_detailed(
            mission_id=mission_id,
            guid=guid,
            client=client,
            body=body,
        )
    ).parsed
