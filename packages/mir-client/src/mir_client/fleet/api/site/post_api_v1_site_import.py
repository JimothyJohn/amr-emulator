from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_v1_site_import_files_body import PostApiV1SiteImportFilesBody
from ...models.post_api_v1_site_import_json_body import PostApiV1SiteImportJsonBody
from ...models.problem_details import ProblemDetails
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PostApiV1SiteImportFilesBody | PostApiV1SiteImportJsonBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/site/import",
    }

    if isinstance(body, PostApiV1SiteImportFilesBody):
        if not isinstance(body, Unset):
            _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data; boundary=+++"
    if isinstance(body, PostApiV1SiteImportJsonBody):
        if not isinstance(body, Unset):
            _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | None:
    if response.status_code == 202:
        response_202 = cast(Any, None)
        return response_202

    if response.status_code == 400:
        response_400 = ProblemDetails.from_dict(response.json())

        return response_400

    if response.status_code == 409:
        response_409 = ProblemDetails.from_dict(response.json())

        return response_409

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
    body: PostApiV1SiteImportFilesBody | PostApiV1SiteImportJsonBody | Unset = UNSET,
) -> Response[Any | ProblemDetails]:
    """Import a site file to MiR Fleet.


    You must submit the file using these headers:

    Content-Type: multipart/form-data

    Content-Disposition: form-date; name=”site-file”

    Args:
        body (PostApiV1SiteImportFilesBody | Unset):
        body (PostApiV1SiteImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
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
    body: PostApiV1SiteImportFilesBody | PostApiV1SiteImportJsonBody | Unset = UNSET,
) -> Any | ProblemDetails | None:
    """Import a site file to MiR Fleet.


    You must submit the file using these headers:

    Content-Type: multipart/form-data

    Content-Disposition: form-date; name=”site-file”

    Args:
        body (PostApiV1SiteImportFilesBody | Unset):
        body (PostApiV1SiteImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1SiteImportFilesBody | PostApiV1SiteImportJsonBody | Unset = UNSET,
) -> Response[Any | ProblemDetails]:
    """Import a site file to MiR Fleet.


    You must submit the file using these headers:

    Content-Type: multipart/form-data

    Content-Disposition: form-date; name=”site-file”

    Args:
        body (PostApiV1SiteImportFilesBody | Unset):
        body (PostApiV1SiteImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1SiteImportFilesBody | PostApiV1SiteImportJsonBody | Unset = UNSET,
) -> Any | ProblemDetails | None:
    """Import a site file to MiR Fleet.


    You must submit the file using these headers:

    Content-Type: multipart/form-data

    Content-Disposition: form-date; name=”site-file”

    Args:
        body (PostApiV1SiteImportFilesBody | Unset):
        body (PostApiV1SiteImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
