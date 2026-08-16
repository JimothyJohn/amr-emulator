from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_position_transition_lists import GetPositionTransitionLists
from ...models.post_position_transition_lists import PostPositionTransitionLists
from ...types import Response


def _get_kwargs(
    *,
    body: PostPositionTransitionLists,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/position_transition_lists",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetPositionTransitionLists | None:
    if response.status_code == 201:
        response_201 = GetPositionTransitionLists.from_dict(response.json())

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
) -> Response[Error | GetPositionTransitionLists]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostPositionTransitionLists,
) -> Response[Error | GetPositionTransitionLists]:
    """
    Args:
        body (PostPositionTransitionLists):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetPositionTransitionLists]
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
    body: PostPositionTransitionLists,
) -> Error | GetPositionTransitionLists | None:
    """
    Args:
        body (PostPositionTransitionLists):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetPositionTransitionLists
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostPositionTransitionLists,
) -> Response[Error | GetPositionTransitionLists]:
    """
    Args:
        body (PostPositionTransitionLists):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetPositionTransitionLists]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostPositionTransitionLists,
) -> Error | GetPositionTransitionLists | None:
    """
    Args:
        body (PostPositionTransitionLists):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetPositionTransitionLists
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
