"""The emulator-only headers were renamed X-MiR-* -> X-AMR-*. Callers of the
hosted endpoint that still send the old spelling must keep working, and the
new spelling wins when both are present."""

from amr_emulator.app import create_app
from amr_emulator.auth import expected_token
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
from starlette.testclient import TestClient

AUTH = {"Authorization": f"Basic {expected_token('distributor', 'distributor')}"}
KEY = {"x-api-key": DEFAULT_API_KEY}
REGISTER = "/api/v2.0.0/registers/7"


def write_register(client: TestClient, value: int, headers: dict) -> None:
    response = client.put(REGISTER, json={"value": value}, headers=headers)
    assert response.status_code == 200, response.text


def read_register(client: TestClient, headers: dict) -> float:
    return client.get(REGISTER, headers=headers).json()["value"]


def test_legacy_session_header_addresses_the_same_robot():
    client = TestClient(create_app())
    write_register(client, 41, {**AUTH, "X-MiR-Session": "old-caller"})
    assert read_register(client, {**AUTH, "X-AMR-Session": "old-caller"}) == 41
    assert read_register(client, {**AUTH, "X-MiR-Session": "old-caller"}) == 41
    assert read_register(client, AUTH) != 41, "default robot untouched"


def test_new_session_header_wins_over_legacy():
    client = TestClient(create_app())
    both = {**AUTH, "X-AMR-Session": "new-name", "X-MiR-Session": "old-name"}
    write_register(client, 17, both)
    assert read_register(client, {**AUTH, "X-AMR-Session": "new-name"}) == 17
    assert read_register(client, {**AUTH, "X-AMR-Session": "old-name"}) != 17


def test_legacy_session_header_is_still_validated():
    client = TestClient(create_app())
    response = client.get(
        "/api/v2.0.0/status", headers={**AUTH, "X-MiR-Session": "no spaces allowed!"}
    )
    assert response.status_code == 400


def test_legacy_latency_header_is_still_validated():
    client = TestClient(create_app())
    response = client.get("/api/v2.0.0/status", headers={**AUTH, "X-MiR-Latency": "-5"})
    assert response.status_code == 400


def test_legacy_mission_duration_header_is_still_validated():
    client = TestClient(create_app())
    missions = client.get("/api/v2.0.0/missions", headers=AUTH).json()
    response = client.post(
        "/api/v2.0.0/mission_queue",
        json={"mission_id": missions[0]["guid"]},
        headers={**AUTH, "X-MiR-Mission-Duration": "not-a-number"},
    )
    assert response.status_code == 400


def test_fleet_honors_the_legacy_session_header():
    fleet = TestClient(create_fleet_app("1.5.0"))
    response = fleet.get("/api/v1/robots", headers={**KEY, "X-MiR-Session": "no spaces allowed!"})
    assert response.status_code == 400
