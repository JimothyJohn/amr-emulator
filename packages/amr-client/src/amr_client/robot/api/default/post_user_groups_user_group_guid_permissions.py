from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_user_group_permission import GetUserGroupPermission
from ...models.post_user_group_permission import PostUserGroupPermission
from ...types import Response


def _get_kwargs(
    user_group_guid: str,
    *,
    body: PostUserGroupPermission,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/user_groups/{user_group_guid}/permissions".format(
            user_group_guid=quote(str(user_group_guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetUserGroupPermission | None:
    if response.status_code == 201:
        response_201 = GetUserGroupPermission.from_dict(response.json())

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
) -> Response[Error | GetUserGroupPermission]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_group_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostUserGroupPermission,
) -> Response[Error | GetUserGroupPermission]:
    """
    Args:
        user_group_guid (str):
        body (PostUserGroupPermission):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetUserGroupPermission]
    """

    kwargs = _get_kwargs(
        user_group_guid=user_group_guid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_group_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostUserGroupPermission,
) -> Error | GetUserGroupPermission | None:
    """
    Args:
        user_group_guid (str):
        body (PostUserGroupPermission):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetUserGroupPermission
    """

    return sync_detailed(
        user_group_guid=user_group_guid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_group_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostUserGroupPermission,
) -> Response[Error | GetUserGroupPermission]:
    """
    Args:
        user_group_guid (str):
        body (PostUserGroupPermission):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetUserGroupPermission]
    """

    kwargs = _get_kwargs(
        user_group_guid=user_group_guid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_group_guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostUserGroupPermission,
) -> Error | GetUserGroupPermission | None:
    """
    Args:
        user_group_guid (str):
        body (PostUserGroupPermission):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetUserGroupPermission
    """

    return (
        await asyncio_detailed(
            user_group_guid=user_group_guid,
            client=client,
            body=body,
        )
    ).parsed
