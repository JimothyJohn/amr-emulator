from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_io_module_status import GetIoModuleStatus
from ...models.post_io_module_status import PostIoModuleStatus
from ...types import Response


def _get_kwargs(
    guid: str,
    *,
    body: PostIoModuleStatus,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/io_modules/{guid}/status".format(
            guid=quote(str(guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetIoModuleStatus | None:
    if response.status_code == 201:
        response_201 = GetIoModuleStatus.from_dict(response.json())

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
) -> Response[Error | GetIoModuleStatus]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostIoModuleStatus,
) -> Response[Error | GetIoModuleStatus]:
    """
    Args:
        guid (str):
        body (PostIoModuleStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetIoModuleStatus]
    """

    kwargs = _get_kwargs(
        guid=guid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostIoModuleStatus,
) -> Error | GetIoModuleStatus | None:
    """
    Args:
        guid (str):
        body (PostIoModuleStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetIoModuleStatus
    """

    return sync_detailed(
        guid=guid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostIoModuleStatus,
) -> Response[Error | GetIoModuleStatus]:
    """
    Args:
        guid (str):
        body (PostIoModuleStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetIoModuleStatus]
    """

    kwargs = _get_kwargs(
        guid=guid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostIoModuleStatus,
) -> Error | GetIoModuleStatus | None:
    """
    Args:
        guid (str):
        body (PostIoModuleStatus):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetIoModuleStatus
    """

    return (
        await asyncio_detailed(
            guid=guid,
            client=client,
            body=body,
        )
    ).parsed
