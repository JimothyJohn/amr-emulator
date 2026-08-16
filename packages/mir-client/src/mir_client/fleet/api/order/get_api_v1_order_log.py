from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_details import ProblemDetails
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    oldest_termination_hour: int | Unset = 1,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["oldestTerminationHour"] = oldest_termination_hour

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/order-log",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 500:
        response_500 = ProblemDetails.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ProblemDetails]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    oldest_termination_hour: int | Unset = 1,
) -> Response[Any | ProblemDetails]:
    """Get order log csv

     Get log of terminated orders, as a CSV file. By default, orders terminated in the last hour are
    included.

    Args:
        oldest_termination_hour (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
    """

    kwargs = _get_kwargs(
        oldest_termination_hour=oldest_termination_hour,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    oldest_termination_hour: int | Unset = 1,
) -> Any | ProblemDetails | None:
    """Get order log csv

     Get log of terminated orders, as a CSV file. By default, orders terminated in the last hour are
    included.

    Args:
        oldest_termination_hour (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return sync_detailed(
        client=client,
        oldest_termination_hour=oldest_termination_hour,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    oldest_termination_hour: int | Unset = 1,
) -> Response[Any | ProblemDetails]:
    """Get order log csv

     Get log of terminated orders, as a CSV file. By default, orders terminated in the last hour are
    included.

    Args:
        oldest_termination_hour (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
    """

    kwargs = _get_kwargs(
        oldest_termination_hour=oldest_termination_hour,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    oldest_termination_hour: int | Unset = 1,
) -> Any | ProblemDetails | None:
    """Get order log csv

     Get log of terminated orders, as a CSV file. By default, orders terminated in the last hour are
    included.

    Args:
        oldest_termination_hour (int | Unset):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            oldest_termination_hour=oldest_termination_hour,
        )
    ).parsed
