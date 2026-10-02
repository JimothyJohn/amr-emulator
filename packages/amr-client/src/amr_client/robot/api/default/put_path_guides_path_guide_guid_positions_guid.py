from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_path_guide_position import GetPathGuidePosition
from ...models.put_path_guide_position import PutPathGuidePosition
from ...types import Response


def _get_kwargs(
    path_guide_guid: str,
    guid: str,
    *,
    body: PutPathGuidePosition,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/path_guides/{path_guide_guid}/positions/{guid}".format(
            path_guide_guid=quote(str(path_guide_guid), safe=""),
            guid=quote(str(guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetPathGuidePosition | None:
    if response.status_code == 200:
        response_200 = GetPathGuidePosition.from_dict(response.json())

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
) -> Response[Error | GetPathGuidePosition]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    path_guide_guid: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutPathGuidePosition,
) -> Response[Error | GetPathGuidePosition]:
    """
    Args:
        path_guide_guid (str):
        guid (str):
        body (PutPathGuidePosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetPathGuidePosition]
    """

    kwargs = _get_kwargs(
        path_guide_guid=path_guide_guid,
        guid=guid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    path_guide_guid: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutPathGuidePosition,
) -> Error | GetPathGuidePosition | None:
    """
    Args:
        path_guide_guid (str):
        guid (str):
        body (PutPathGuidePosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetPathGuidePosition
    """

    return sync_detailed(
        path_guide_guid=path_guide_guid,
        guid=guid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    path_guide_guid: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutPathGuidePosition,
) -> Response[Error | GetPathGuidePosition]:
    """
    Args:
        path_guide_guid (str):
        guid (str):
        body (PutPathGuidePosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetPathGuidePosition]
    """

    kwargs = _get_kwargs(
        path_guide_guid=path_guide_guid,
        guid=guid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    path_guide_guid: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutPathGuidePosition,
) -> Error | GetPathGuidePosition | None:
    """
    Args:
        path_guide_guid (str):
        guid (str):
        body (PutPathGuidePosition):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetPathGuidePosition
    """

    return (
        await asyncio_detailed(
            path_guide_guid=path_guide_guid,
            guid=guid,
            client=client,
            body=body,
        )
    ).parsed
