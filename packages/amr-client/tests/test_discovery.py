"""Connect-time discovery against real emulator apps — no mocked servers.

Every classification path runs against the actual Starlette applications
(robot, fleet, multi-version dispatcher) over in-process ASGI, plus
hand-built hostile/degraded servers for the fallback probes a real MiR
robot would exercise (no index, no swagger, HTML landing pages).
"""

from __future__ import annotations

import asyncio

import httpx
import pytest
from amr_client import (
    DiscoveryError,
    client_for,
    detect_server_async,
    provenance,
)
from amr_client.discovery import ServerInfo, _interpret
from amr_emulator import registry
from amr_emulator.app import create_app
from amr_emulator.fleet import create_fleet_app
from amr_emulator.serverless import build_app
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route


def run(coro):
    return asyncio.run(coro)


def detect(app) -> ServerInfo:
    return run(detect_server_async("http://target.test", transport=httpx.ASGITransport(app=app)))


@pytest.mark.parametrize("version", registry.supported_versions())
def test_detects_every_tracked_robot_version(version):
    info = detect(create_app(version))
    assert info.kind == "robot"
    assert info.version == version
    assert info.api_prefix == "/api/v2.0.0"


@pytest.mark.parametrize("version", registry.fleet_supported_versions())
def test_detects_every_tracked_fleet_version(version):
    info = detect(create_fleet_app(version))
    assert info.kind == "fleet"
    assert info.version == version
    assert info.api_prefix == "/api/v1"


def test_detects_the_multi_version_dispatcher():
    info = detect(build_app())
    assert info.kind == "dispatcher"
    assert info.versions == tuple(registry.supported_versions())
    assert info.fleet_versions == tuple(registry.fleet_supported_versions())
    assert info.latest == registry.supported_versions()[0]


def test_detection_needs_no_credentials():
    # Auth enforced (the default) must not block the handshake.
    info = detect(create_app(enforce_auth=True))
    assert info.kind == "robot"
    assert info.version == registry.supported_versions()[0]


def _bare_server(routes) -> Starlette:
    return Starlette(routes=routes)


def test_html_index_falls_through_to_the_fleet_version_endpoint():
    # Shaped like a real MiR Fleet: "/" serves a web UI, not JSON; the
    # official /api/v1/system/version endpoint is the one that answers.
    async def ui(_request):
        return HTMLResponse("<html>MiR Fleet</html>")

    async def version(_request):
        return JSONResponse({"version": "1.4.2", "fleet-name": "Shopfloor"})

    info = detect(_bare_server([Route("/", ui), Route("/api/v1/system/version", version)]))
    assert info == ServerInfo("fleet", "1.4.2", "http://target.test", "/api/v1")


def test_swagger_only_robot_reports_its_spec_version():
    async def swagger(_request):
        return JSONResponse({"swagger": "2.0", "info": {"version": "2.13.5.4"}, "paths": {}})

    info = detect(_bare_server([Route("/swagger.json", swagger)]))
    assert info.kind == "robot"
    assert info.version == "2.13.5.4"


def test_auth_walled_robot_is_recognized_with_unknown_version():
    # A locked-down real robot: /status is behind MiR auth and 401s. A 401 at
    # exactly this path is a strong signal; version is honestly unknown.
    async def status(_request):
        return JSONResponse({"error_code": "401"}, status_code=401)

    info = detect(_bare_server([Route("/api/v2.0.0/status", status)]))
    assert info == ServerInfo("robot", None, "http://target.test", "/api/v2.0.0")


def test_open_robot_with_a_real_status_body_is_recognized():
    # Auth-disabled robot: 200 with an actual MiR status document.
    async def status(_request):
        return JSONResponse({"state_id": 3, "state_text": "Ready", "battery_percentage": 91})

    info = detect(_bare_server([Route("/api/v2.0.0/status", status)]))
    assert info == ServerInfo("robot", None, "http://target.test", "/api/v2.0.0")


def test_server_that_200s_everything_is_not_a_robot():
    # The decoy that breaks a naive fallback: 200 + JSON on every path,
    # including /api/v2.0.0/status, but no MiR status fields.
    async def anything(_request):
        return JSONResponse({"hello": "world"})

    with pytest.raises(DiscoveryError, match="no probe identified"):
        detect(
            _bare_server(
                [
                    Route("/api/v2.0.0/status", anything),
                    Route("/{path:path}", anything),
                ]
            )
        )


def test_non_mir_server_raises_instead_of_guessing():
    async def home(_request):
        return JSONResponse({"hello": "world"})

    with pytest.raises(DiscoveryError, match="no probe identified"):
        detect(_bare_server([Route("/", home)]))


def test_unreachable_host_raises_with_the_transport_error():
    class Down(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            raise httpx.ConnectError("boom", request=request)

    with pytest.raises(DiscoveryError, match="cannot reach"):
        run(detect_server_async("http://target.test", transport=Down()))


def test_foreign_healthz_does_not_masquerade_as_a_dispatcher():
    # Plenty of services expose /healthz; without a versions manifest it
    # must not classify, and probing continues to the robot fallback.
    async def healthz(_request):
        return JSONResponse({"status": "ok"})

    async def status(_request):
        return JSONResponse({"state_id": 3, "state_text": "Ready"}, status_code=200)

    info = detect(_bare_server([Route("/healthz", healthz), Route("/api/v2.0.0/status", status)]))
    assert info.kind == "robot"


@pytest.mark.parametrize(
    "doc",
    [None, [], "3.8.1", {"versions": "3.8.1"}, {"versions": [1, 2]}, {"info": {}}],
)
def test_interpret_rejects_malformed_bodies(doc):
    for probe in ("healthz", "index", "fleet_version", "swagger"):
        assert _interpret(probe, 200, doc, "http://x") is None


# --- client_for: turning a detection into the right client -----------------


def _dispatcher_info() -> ServerInfo:
    return detect(build_app())


def test_client_for_dispatcher_defaults_to_the_newest_robot():
    client = client_for(_dispatcher_info())
    latest = registry.supported_versions()[0]
    assert str(client._base_url) == f"http://target.test/{latest}/api/v2.0.0"


def test_client_for_dispatcher_resolves_a_requested_robot_version():
    version = registry.supported_versions()[-1]  # oldest tracked
    client = client_for(_dispatcher_info(), version=version)
    assert str(client._base_url) == f"http://target.test/{version}/api/v2.0.0"


def test_client_for_dispatcher_resolves_a_fleet_version_mount():
    version = registry.fleet_supported_versions()[0]
    client = client_for(_dispatcher_info(), version=version)
    assert str(client._base_url) == f"http://target.test/fleet/{version}"


def test_client_for_dispatcher_rejects_an_unserved_version():
    with pytest.raises(DiscoveryError, match=r"does not serve 9\.9\.9"):
        client_for(_dispatcher_info(), version="9.9.9")


def test_client_for_rejects_a_version_the_robot_does_not_run():
    info = ServerInfo("robot", "3.8.1", "http://target.test", "/api/v2.0.0")
    with pytest.raises(DiscoveryError, match="cannot"):
        client_for(info, version="2.14.7")


def test_client_for_warns_when_robot_major_differs_from_the_generated_spec():
    info = ServerInfo("robot", "2.14.7", "http://target.test", "/api/v2.0.0")
    with pytest.warns(UserWarning, match=provenance.ROBOT_VERSION):
        client_for(info)


def test_client_for_stays_quiet_within_the_generated_major():
    import warnings as _warnings

    info = ServerInfo("robot", "3.7.2", "http://target.test", "/api/v2.0.0")
    with _warnings.catch_warnings():
        _warnings.simplefilter("error")
        client_for(info)


def test_detect_then_drive_end_to_end():
    """The whole promise: point at an unknown target, get a working client."""
    from amr_client.robot.api.default import get_status
    from amr_client.robot.client import AuthenticatedClient as RobotClient

    app = create_app()
    transport = httpx.ASGITransport(app=app)
    info = run(detect_server_async("http://target.test", transport=transport))
    client = client_for(info, transport=transport)
    assert isinstance(client, RobotClient)
    status = run(get_status.asyncio(client=client))
    assert status.state_text == "Ready"
