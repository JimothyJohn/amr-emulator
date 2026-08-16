from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_v1_missions_import_files_body import PostApiV1MissionsImportFilesBody
from ...models.post_api_v1_missions_import_json_body import PostApiV1MissionsImportJsonBody
from ...models.problem_details import ProblemDetails
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PostApiV1MissionsImportFilesBody | PostApiV1MissionsImportJsonBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/missions/import",
    }

    if isinstance(body, PostApiV1MissionsImportFilesBody):
        if not isinstance(body, Unset):
            _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data; boundary=+++"
    if isinstance(body, PostApiV1MissionsImportJsonBody):
        if not isinstance(body, Unset):
            _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ProblemDetails | list[str] | None:
    if response.status_code == 202:
        response_202 = cast(list[str], response.json())

        return response_202

    if response.status_code == 400:
        response_400 = ProblemDetails.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = ProblemDetails.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ProblemDetails | list[str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1MissionsImportFilesBody | PostApiV1MissionsImportJsonBody | Unset = UNSET,
) -> Response[ProblemDetails | list[str]]:
    """Import missions


    Upload a .mission file to MiR Fleet to import missions you exported from another MiR Fleet
    application.

    This feature is only supported in the API. You cannot import or export missions through the MiR
    Fleet interface.

    Args:
        body (PostApiV1MissionsImportFilesBody | Unset):
        body (PostApiV1MissionsImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProblemDetails | list[str]]
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
    body: PostApiV1MissionsImportFilesBody | PostApiV1MissionsImportJsonBody | Unset = UNSET,
) -> ProblemDetails | list[str] | None:
    """Import missions


    Upload a .mission file to MiR Fleet to import missions you exported from another MiR Fleet
    application.

    This feature is only supported in the API. You cannot import or export missions through the MiR
    Fleet interface.

    Args:
        body (PostApiV1MissionsImportFilesBody | Unset):
        body (PostApiV1MissionsImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProblemDetails | list[str]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1MissionsImportFilesBody | PostApiV1MissionsImportJsonBody | Unset = UNSET,
) -> Response[ProblemDetails | list[str]]:
    """Import missions


    Upload a .mission file to MiR Fleet to import missions you exported from another MiR Fleet
    application.

    This feature is only supported in the API. You cannot import or export missions through the MiR
    Fleet interface.

    Args:
        body (PostApiV1MissionsImportFilesBody | Unset):
        body (PostApiV1MissionsImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProblemDetails | list[str]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1MissionsImportFilesBody | PostApiV1MissionsImportJsonBody | Unset = UNSET,
) -> ProblemDetails | list[str] | None:
    """Import missions


    Upload a .mission file to MiR Fleet to import missions you exported from another MiR Fleet
    application.

    This feature is only supported in the API. You cannot import or export missions through the MiR
    Fleet interface.

    Args:
        body (PostApiV1MissionsImportFilesBody | Unset):
        body (PostApiV1MissionsImportJsonBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProblemDetails | list[str]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
