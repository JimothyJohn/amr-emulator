from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_io_module import GetIoModule
from ...models.put_io_module import PutIoModule
from ...types import Response


def _get_kwargs(
    guid: str,
    *,
    body: PutIoModule,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/io_modules/{guid}".format(
            guid=quote(str(guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetIoModule | None:
    if response.status_code == 200:
        response_200 = GetIoModule.from_dict(response.json())

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
) -> Response[Error | GetIoModule]:
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
    body: PutIoModule,
) -> Response[Error | GetIoModule]:
    """
    Args:
        guid (str):
        body (PutIoModule):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetIoModule]
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
    body: PutIoModule,
) -> Error | GetIoModule | None:
    """
    Args:
        guid (str):
        body (PutIoModule):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetIoModule
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
    body: PutIoModule,
) -> Response[Error | GetIoModule]:
    """
    Args:
        guid (str):
        body (PutIoModule):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetIoModule]
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
    body: PutIoModule,
) -> Error | GetIoModule | None:
    """
    Args:
        guid (str):
        body (PutIoModule):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetIoModule
    """

    return (
        await asyncio_detailed(
            guid=guid,
            client=client,
            body=body,
        )
    ).parsed
