"""Error responses stay machine-readable JSON on every app, every status.

Regression for a gap the fuzz suite exposed: a path parameter of ``..``
URL-normalizes onto a sibling route where the method isn't allowed, and the
robot and serverless apps answered with Starlette's default plain-text 405
("Method Not Allowed") — the fleet app had the JSON handler, the other two
did not. The contract under test: any 4xx from any app parses as JSON and
carries ``error_code``.
"""

from mir_emulator import serverless
from mir_emulator.app import create_app
from mir_emulator.fleet import create_fleet_app
from starlette.testclient import TestClient


def _assert_json_405(client, method: str, url: str) -> None:
    response = client.request(method, url)
    assert response.status_code == 405, f"{method} {url} -> {response.status_code}"
    body = response.json()
    assert "error_code" in body


def test_robot_app_405_is_json():
    app = create_app()
    base = app.state.emulator.spec.base_path
    with TestClient(app, base_url="http://emulator.test") as client:
        _assert_json_405(client, "POST", f"{base}/actions")
        # the fuzz-found shape: a `..` path param normalized onto another
        # route — whatever 4xx it lands on must still be JSON
        response = client.get(f"{base}/actions/../")
        assert 400 <= response.status_code < 500
        assert "error_code" in response.json()


def test_fleet_app_405_is_json():
    app = create_fleet_app()
    with TestClient(app, base_url="http://emulator.test") as client:
        _assert_json_405(client, "DELETE", "/")


def test_serverless_app_405_is_json():
    app = serverless.build_app()
    with TestClient(app, base_url="http://emulator.test") as client:
        response = client.request("DELETE", "/")
        assert response.status_code == 405
        assert "error_code" in response.json()
