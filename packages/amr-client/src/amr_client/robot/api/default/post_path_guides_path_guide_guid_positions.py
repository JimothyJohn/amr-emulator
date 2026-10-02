from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_path_guide_positions import GetPathGuidePositions
from ...models.post_path_guide_positions import PostPathGuidePositions
from ...types import Response


def _get_kwargs(
    path_guide_guid: str,
    *,
    body: PostPathGuidePositions,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/path_guides/{path_guide_guid}/positions".format(
            path_guide_guid=quote(str(path_guide_guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetPathGuidePositions | None:
    if response.status_code == 201:
        response_201 = GetPathGuidePositions.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())

        return response_409

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | GetPathGuidePositions]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    path_guide_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostPathGuidePositions,
) -> Response[Error | GetPathGuidePositions]:
    """
    Args:
        path_guide_guid (str):
        body (PostPathGuidePositions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetPathGuidePositions]
    """

    kwargs = _get_kwargs(
        path_guide_guid=path_guide_guid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    path_guide_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostPathGuidePositions,
) -> Error | GetPathGuidePositions | None:
    """
    Args:
        path_guide_guid (str):
        body (PostPathGuidePositions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetPathGuidePositions
    """

    return sync_detailed(
        path_guide_guid=path_guide_guid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    path_guide_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostPathGuidePositions,
) -> Response[Error | GetPathGuidePositions]:
    """
    Args:
        path_guide_guid (str):
        body (PostPathGuidePositions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetPathGuidePositions]
    """

    kwargs = _get_kwargs(
        path_guide_guid=path_guide_guid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    path_guide_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostPathGuidePositions,
) -> Error | GetPathGuidePositions | None:
    """
    Args:
        path_guide_guid (str):
        body (PostPathGuidePositions):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetPathGuidePositions
    """

    return (
        await asyncio_detailed(
            path_guide_guid=path_guide_guid,
            client=client,
            body=body,
        )
    ).parsed
