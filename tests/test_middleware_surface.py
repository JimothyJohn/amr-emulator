"""The emulator as middleware: spec endpoints, security headers, CORS."""

from amr_emulator.app import create_app
from starlette.testclient import TestClient

from tests.conftest import AUTH_HEADER


def test_serves_both_spec_flavors(client, spec):
    swagger = client.get("/swagger.json").json()
    assert swagger.get("swagger") == "2.0" or str(swagger.get("openapi", "")).startswith("3")

    openapi = client.get("/openapi.json").json()
    assert str(openapi.get("openapi", "")).startswith("3")
    assert openapi["info"]["version"] == spec.mir_version
    assert len(openapi["paths"]) == len({p for _m, p in spec.operations})


def test_index_links_specs(client, spec):
    body = client.get("/").json()
    assert body["specs"] == {"swagger2": "/swagger.json", "openapi3": "/openapi.json"}


def test_index_identifies_kind_and_version(client, spec):
    """The unauthenticated index is the connect-time discovery surface:
    clients read kind + version here instead of assuming an installed one."""
    body = client.get("/").json()
    assert body["kind"] == "robot"
    assert body["emulated_mir_version"] == spec.mir_version
    assert body["base_path"] == spec.base_path


def test_security_headers_on_every_response(client, spec):
    for url in ["/", "/swagger.json", f"{spec.base_path}/status", "/nope"]:
        response = client.get(url, headers=AUTH_HEADER)
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-frame-options"] == "DENY"


def test_cors_disabled_by_default(client, spec):
    response = client.get("/", headers={"Origin": "http://dashboard.example"})
    assert "access-control-allow-origin" not in response.headers


def test_cors_opt_in(mir_version):
    app = create_app(mir_version, cors=True)
    with TestClient(app, base_url="http://emulator.test") as client:
        response = client.get("/", headers={"Origin": "http://dashboard.example"})
        assert response.headers["access-control-allow-origin"] == "*"
        preflight = client.options(
            f"{app.state.emulator.spec.base_path}/status",
            headers={
                "Origin": "http://dashboard.example",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )
        assert preflight.status_code == 200
