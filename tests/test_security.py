"""Negative-path and adversarial tests, run against every tracked version."""

import concurrent.futures

import pytest
from amr_emulator import auth
from amr_emulator.app import create_app
from starlette.testclient import TestClient

from tests.conftest import AUTH_HEADER


def test_no_auth_header_is_rejected_everywhere(client, spec):
    sample = list(spec.operations.values())[:25]
    for op in sample:
        path = op.path
        for name in op.path_param_types():
            path = path.replace("{" + name + "}", "1")
        response = client.request(op.method, spec.base_path + path)
        assert response.status_code == 401, f"{op.method} {op.path} served without auth"
        assert "error_code" in response.json()


def test_wrong_password_rejected(client, spec):
    header = {"Authorization": f"Basic {auth.expected_token('distributor', 'wrong')}"}
    assert client.get(f"{spec.base_path}/status", headers=header).status_code == 401


def test_plain_basic_auth_rejected(client, spec):
    # base64(user:password) without the SHA-256 step must not work.
    import base64

    raw = base64.b64encode(b"distributor:distributor").decode()
    response = client.get(f"{spec.base_path}/status", headers={"Authorization": f"Basic {raw}"})
    assert response.status_code == 401


def test_invalid_json_body_is_400(client, spec):
    response = client.post(
        f"{spec.base_path}/mission_queue",
        content=b'{"mission_id": ',
        headers={**AUTH_HEADER, "Content-Type": "application/json"},
    )
    assert response.status_code == 400


def test_schema_violating_body_is_400(client, spec):
    response = client.post(
        f"{spec.base_path}/mission_queue",
        json={"mission_id": 12345},  # spec requires a string guid
        headers=AUTH_HEADER,
    )
    assert response.status_code == 400


def test_oversized_body_is_rejected(client, spec):
    blob = b'{"mission_id": "' + b"A" * (3 * 1024 * 1024) + b'"}'
    response = client.post(
        f"{spec.base_path}/mission_queue",
        content=blob,
        headers={**AUTH_HEADER, "Content-Type": "application/json"},
    )
    assert response.status_code == 400


def test_unknown_paths_are_json_404(client, spec):
    for path in ["/api/v2.0.0/definitely_not_real", "/api/v2.0.0/", "/etc/passwd"]:
        response = client.get(path, headers=AUTH_HEADER)
        assert response.status_code == 404
        assert response.json()["error_code"] == "404"


def test_path_traversal_does_not_escape(client, spec):
    response = client.get(
        f"{spec.base_path}/missions/..%2F..%2F..%2Fetc%2Fpasswd", headers=AUTH_HEADER
    )
    assert response.status_code in (400, 404)
    body = response.content.decode(errors="replace")
    assert "root:" not in body


def test_wrong_method_is_405_or_404(client, spec):
    response = client.request("DELETE", f"{spec.base_path}/status", headers=AUTH_HEADER)
    assert response.status_code in (404, 405)


def test_error_bodies_do_not_leak_internals(client, spec):
    response = client.post(
        f"{spec.base_path}/mission_queue",
        content=b"\xff\xfe not json",
        headers={**AUTH_HEADER, "Content-Type": "application/json"},
    )
    text = response.text
    for needle in ["Traceback", "starlette", "site-packages", "/Users/", "/home/"]:
        assert needle not in text


def test_injected_newlines_in_body_do_not_corrupt_responses(client, spec):
    hostile = "evil\r\nSet-Cookie: pwned=1\r\n\x1b[31mANSI"
    response = client.post(
        f"{spec.base_path}/missions",
        json={"name": hostile, "group_id": "emulated-0000-0000-0001-000000000000"},
        headers=AUTH_HEADER,
    )
    assert "set-cookie" not in response.headers
    if response.status_code < 300:
        # the hostile string must come back JSON-escaped, not raw
        assert response.json()["name"] == hostile


@pytest.mark.parametrize("workers", [16])
def test_parallel_register_writes_are_not_lost(mir_version, workers):
    app = create_app(mir_version)
    with TestClient(app, base_url="http://emulator.test") as client:
        base = f"{app.state.emulator.spec.base_path}/registers"

        def write(i: int) -> int:
            response = client.put(f"{base}/{i}", json={"value": float(i)}, headers=AUTH_HEADER)
            return response.status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            statuses = list(pool.map(write, range(1, 101)))
        assert set(statuses) == {200}

        values = {r["id"]: r["value"] for r in client.get(base, headers=AUTH_HEADER).json()}
        for i in range(1, 101):
            assert values[i] == float(i), f"register {i} write was lost"


def test_parallel_mission_queue_posts_get_unique_ids(mir_version):
    app = create_app(mir_version)
    with TestClient(app, base_url="http://emulator.test") as client:
        base = app.state.emulator.spec.base_path

        def enqueue(_: int) -> int:
            response = client.post(
                f"{base}/mission_queue",
                json={"mission_id": "emulated-0000-0000-0001-000000000000"},
                headers=AUTH_HEADER,
            )
            assert response.status_code < 300
            return response.json()["id"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            ids = list(pool.map(enqueue, range(40)))
        assert len(set(ids)) == 40, "duplicate mission queue ids under concurrency"
