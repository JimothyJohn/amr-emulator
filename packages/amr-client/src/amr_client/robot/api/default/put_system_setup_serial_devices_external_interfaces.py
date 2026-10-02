from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_setup_external_interface_serials import GetSetupExternalInterfaceSerials
from ...models.put_setup_external_interface_serials import PutSetupExternalInterfaceSerials
from ...types import Response


def _get_kwargs(
    *,
    body: PutSetupExternalInterfaceSerials,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/system/setup/serial_devices/external_interfaces",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetSetupExternalInterfaceSerials | None:
    if response.status_code == 200:
        response_200 = GetSetupExternalInterfaceSerials.from_dict(response.json())

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
) -> Response[Error | GetSetupExternalInterfaceSerials]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PutSetupExternalInterfaceSerials,
) -> Response[Error | GetSetupExternalInterfaceSerials]:
    """
    Args:
        body (PutSetupExternalInterfaceSerials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetSetupExternalInterfaceSerials]
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
    body: PutSetupExternalInterfaceSerials,
) -> Error | GetSetupExternalInterfaceSerials | None:
    """
    Args:
        body (PutSetupExternalInterfaceSerials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetSetupExternalInterfaceSerials
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PutSetupExternalInterfaceSerials,
) -> Response[Error | GetSetupExternalInterfaceSerials]:
    """
    Args:
        body (PutSetupExternalInterfaceSerials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetSetupExternalInterfaceSerials]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PutSetupExternalInterfaceSerials,
) -> Error | GetSetupExternalInterfaceSerials | None:
    """
    Args:
        body (PutSetupExternalInterfaceSerials):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetSetupExternalInterfaceSerials
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
