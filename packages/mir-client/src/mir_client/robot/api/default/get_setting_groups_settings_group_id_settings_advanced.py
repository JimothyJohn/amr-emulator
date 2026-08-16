from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_setting_group_advanced_settings import GetSettingGroupAdvancedSettings
from ...types import Response


def _get_kwargs(
    settings_group_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/setting_groups/{settings_group_id}/settings/advanced".format(
            settings_group_id=quote(str(settings_group_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | list[GetSettingGroupAdvancedSettings] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetSettingGroupAdvancedSettings.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Error | list[GetSettingGroupAdvancedSettings]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    settings_group_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[GetSettingGroupAdvancedSettings]]:
    """
    Args:
        settings_group_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[GetSettingGroupAdvancedSettings]]
    """

    kwargs = _get_kwargs(
        settings_group_id=settings_group_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    settings_group_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[GetSettingGroupAdvancedSettings] | None:
    """
    Args:
        settings_group_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[GetSettingGroupAdvancedSettings]
    """

    return sync_detailed(
        settings_group_id=settings_group_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    settings_group_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | list[GetSettingGroupAdvancedSettings]]:
    """
    Args:
        settings_group_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[GetSettingGroupAdvancedSettings]]
    """

    kwargs = _get_kwargs(
        settings_group_id=settings_group_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    settings_group_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Error | list[GetSettingGroupAdvancedSettings] | None:
    """
    Args:
        settings_group_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[GetSettingGroupAdvancedSettings]
    """

    return (
        await asyncio_detailed(
            settings_group_id=settings_group_id,
            client=client,
        )
    ).parsed
