from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_dashboard_widget import GetDashboardWidget
from ...models.put_dashboard_widget import PutDashboardWidget
from ...types import Response


def _get_kwargs(
    dashboard_id: str,
    guid: str,
    *,
    body: PutDashboardWidget,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/dashboards/{dashboard_id}/widgets/{guid}".format(
            dashboard_id=quote(str(dashboard_id), safe=""),
            guid=quote(str(guid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetDashboardWidget | None:
    if response.status_code == 200:
        response_200 = GetDashboardWidget.from_dict(response.json())

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
) -> Response[Error | GetDashboardWidget]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dashboard_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutDashboardWidget,
) -> Response[Error | GetDashboardWidget]:
    """
    Args:
        dashboard_id (str):
        guid (str):
        body (PutDashboardWidget):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetDashboardWidget]
    """

    kwargs = _get_kwargs(
        dashboard_id=dashboard_id,
        guid=guid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    dashboard_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutDashboardWidget,
) -> Error | GetDashboardWidget | None:
    """
    Args:
        dashboard_id (str):
        guid (str):
        body (PutDashboardWidget):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetDashboardWidget
    """

    return sync_detailed(
        dashboard_id=dashboard_id,
        guid=guid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    dashboard_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutDashboardWidget,
) -> Response[Error | GetDashboardWidget]:
    """
    Args:
        dashboard_id (str):
        guid (str):
        body (PutDashboardWidget):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetDashboardWidget]
    """

    kwargs = _get_kwargs(
        dashboard_id=dashboard_id,
        guid=guid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    dashboard_id: str,
    guid: str,
    *,
    client: AuthenticatedClient | Client,
    body: PutDashboardWidget,
) -> Error | GetDashboardWidget | None:
    """
    Args:
        dashboard_id (str):
        guid (str):
        body (PutDashboardWidget):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetDashboardWidget
    """

    return (
        await asyncio_detailed(
            dashboard_id=dashboard_id,
            guid=guid,
            client=client,
            body=body,
        )
    ).parsed
