from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_cart_calibration import GetCartCalibration
from ...models.put_cart_calibration import PutCartCalibration
from ...types import Response


def _get_kwargs(
    guid: str,
    *,
    body: PutCartCalibration,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/cart_calibrations/{guid}".format(
            guid=quote(str(guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetCartCalibration | None:
    if response.status_code == 200:
        response_200 = GetCartCalibration.from_dict(response.json())

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
) -> Response[Error | GetCartCalibration]:
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
    body: PutCartCalibration,
) -> Response[Error | GetCartCalibration]:
    """
    Args:
        guid (str):
        body (PutCartCalibration):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetCartCalibration]
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
    body: PutCartCalibration,
) -> Error | GetCartCalibration | None:
    """
    Args:
        guid (str):
        body (PutCartCalibration):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetCartCalibration
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
    body: PutCartCalibration,
) -> Response[Error | GetCartCalibration]:
    """
    Args:
        guid (str):
        body (PutCartCalibration):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetCartCalibration]
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
    body: PutCartCalibration,
) -> Error | GetCartCalibration | None:
    """
    Args:
        guid (str):
        body (PutCartCalibration):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetCartCalibration
    """

    return (
        await asyncio_detailed(
            guid=guid,
            client=client,
            body=body,
        )
    ).parsed
