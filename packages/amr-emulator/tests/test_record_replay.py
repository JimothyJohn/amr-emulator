"""Scenario record & replay: a captured session must reproduce byte-identically
against a fresh emulator, because replay re-freezes the clock to each recorded
instant and the whole simulation is time-derived."""

import json

import pytest
from amr_emulator import behaviors
from amr_emulator.app import create_app
from amr_emulator.auth import expected_token
from amr_emulator.cli import main as cli_main
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
from amr_emulator.record import replay
from starlette.testclient import TestClient

AUTH = {"Authorization": f"Basic {expected_token('distributor', 'distributor')}"}
KEY = {"x-api-key": DEFAULT_API_KEY}
T0 = 1_750_000_000.0


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def tick(self, seconds: float) -> None:
        self.now += seconds

    def __call__(self) -> float:
        return self.now


@pytest.fixture()
def clock(monkeypatch):
    c = Clock()
    monkeypatch.setattr(behaviors, "_now", c)
    return c


def record_robot_session(clock) -> dict:
    """Drive a full mission lifecycle while recording."""
    client = TestClient(create_app("3.8.1"))
    assert (
        client.put("/_emulator/recorder", headers=AUTH, json={"recording": True}).status_code == 200
    )

    mission = client.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    client.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)
    client.get("/api/v2.0.0/status", headers=AUTH)
    clock.tick(10.0)
    client.get("/api/v2.0.0/mission_queue", headers=AUTH)
    client.get("/api/v2.0.0/status", headers=AUTH)

    doc = client.get("/_emulator/recorder", headers=AUTH).json()
    assert doc["recording"] is True
    return doc


def test_recorded_robot_session_replays_byte_identically(clock):
    scenario = record_robot_session(clock)
    assert len(scenario["steps"]) == 5  # missions, enqueue, status, queue, status
    assert replay(scenario) == []


def test_replay_detects_a_regression(clock):
    scenario = record_robot_session(clock)
    scenario["steps"][2]["response"]["battery_percentage"] = 55.0  # tampered
    problems = replay(scenario)
    assert len(problems) == 1
    assert "GET /api/v2.0.0/status" in problems[0]


def test_replay_detects_a_status_change(clock):
    scenario = record_robot_session(clock)
    scenario["steps"][1]["status"] = 409
    assert any("status" in p for p in replay(scenario))


def test_recorder_is_off_by_default_and_clearable(clock):
    client = TestClient(create_app("3.8.1"))
    client.get("/api/v2.0.0/status", headers=AUTH)
    doc = client.get("/_emulator/recorder", headers=AUTH).json()
    assert doc["recording"] is False and doc["steps"] == []

    client.put("/_emulator/recorder", headers=AUTH, json={"recording": True})
    client.get("/api/v2.0.0/status", headers=AUTH)
    cleared = client.delete("/_emulator/recorder", headers=AUTH).json()
    assert cleared["recording"] is False and cleared["steps"] == []


def test_recorder_requires_auth_and_valid_body(clock):
    client = TestClient(create_app("3.8.1"))
    assert client.get("/_emulator/recorder").status_code == 401
    bad = client.put("/_emulator/recorder", headers=AUTH, json={"recording": "yes"})
    assert bad.status_code == 400


def test_recordings_are_session_isolated(clock):
    client = TestClient(create_app("3.8.1"))
    session = {**AUTH, "X-AMR-Session": "crew-a"}
    client.put("/_emulator/recorder", headers=session, json={"recording": True})
    client.get("/api/v2.0.0/status", headers=session)
    client.get("/api/v2.0.0/status", headers=AUTH)  # default robot, not recorded
    doc = client.get("/_emulator/recorder", headers=session).json()
    assert len(doc["steps"]) == 1
    assert client.get("/_emulator/recorder", headers=AUTH).json()["steps"] == []


def test_control_endpoints_are_not_recorded(clock):
    client = TestClient(create_app("3.8.1"))
    client.put("/_emulator/recorder", headers=AUTH, json={"recording": True})
    client.get("/_emulator/faults", headers=AUTH)
    client.get("/_emulator/recorder", headers=AUTH)
    doc = client.get("/_emulator/recorder", headers=AUTH).json()
    assert doc["steps"] == []


def test_fleet_scenario_round_trips(clock):
    client = TestClient(create_fleet_app("1.5.0"))
    client.put("/_emulator/recorder", headers=KEY, json={"recording": True})
    mission = client.get("/api/v1/site/mission", headers=KEY).json()["missions"][0]["id"]
    client.post(
        "/api/v1/serial-order",
        headers=KEY,
        json={"serial-order": {"phases": [{"mission-id": mission}]}},
    )
    clock.tick(3.0)
    client.get("/api/v1/order", headers=KEY)
    scenario = client.get("/_emulator/recorder", headers=KEY).json()
    assert scenario["family"] == "fleet"
    assert len(scenario["steps"]) == 3
    assert replay(scenario) == []


def test_cli_replay_reports_success_and_failure(clock, tmp_path, capsys):
    scenario = record_robot_session(clock)
    good = tmp_path / "good.json"
    good.write_text(json.dumps(scenario))
    assert cli_main(["--replay", str(good)]) == 0
    assert "reproduced exactly" in capsys.readouterr().out

    scenario["steps"][2]["response"]["battery_percentage"] = 55.0
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(scenario))
    assert cli_main(["--replay", str(bad)]) == 1
    assert "mismatches" in capsys.readouterr().out


def test_replay_rejects_foreign_documents():
    assert replay({}) != []
    assert replay({"amr_emulator_scenario": 99, "steps": [{}]}) != []
    assert replay({"amr_emulator_scenario": 1, "steps": []}) != []
