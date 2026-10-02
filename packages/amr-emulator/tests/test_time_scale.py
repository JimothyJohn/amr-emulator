"""Time scaling: simulated time runs Nx wall speed, timestamps stay realistic.

/_emulator/clock replaces the "make everything artificially fast" workflow
(--mission-duration 3, charge_rate 5%/s): missions and battery curves keep
their real-world simulated lengths, the wall wait shrinks. The scaled clock
is anchored at the current simulated instant, so changing scale never jumps
or rewinds time — mission histories derived from stored timestamps survive.

Deterministic like test_mission_sim: the wall clock is a frozen fake that
tests step manually.
"""

from datetime import datetime

import pytest
from amr_emulator import behaviors
from amr_emulator.app import create_app
from amr_emulator.auth import expected_token
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
from starlette.testclient import TestClient

AUTH = {"Authorization": f"Basic {expected_token('distributor', 'distributor')}"}
KEY = {"x-api-key": DEFAULT_API_KEY}
T0 = 1_750_000_000.0


class Wall:
    def __init__(self, start: float = T0) -> None:
        self.now = start

    def tick(self, seconds: float) -> None:
        self.now += seconds

    def __call__(self) -> float:
        return self.now


@pytest.fixture()
def wall(monkeypatch):
    """Fake wall clock; also resets the process-wide scale after each test
    (set_time_scale mutates module globals that monkeypatch cannot see)."""
    w = Wall()
    monkeypatch.setattr(behaviors, "_wall_clock", w)
    monkeypatch.setattr(behaviors, "_now", w)
    yield w
    behaviors._time_scale = 1.0


@pytest.fixture()
def client(wall):
    return TestClient(create_app("3.8.1"))


def _iso_seconds(a: str, b: str) -> float:
    fmt = "%Y-%m-%dT%H:%M:%S"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds()


# --- clock math ---------------------------------------------------------------


def test_sim_time_advances_scale_times_wall(wall):
    assert behaviors.set_time_scale({"scale": 60}) is None
    t0 = behaviors._now()
    wall.tick(2)
    assert behaviors._now() == pytest.approx(t0 + 120)


def test_rescale_keeps_sim_time_continuous(wall):
    behaviors.set_time_scale({"scale": 60})
    wall.tick(10)  # sim advanced 600 s past wall
    t1 = behaviors._now()
    behaviors.set_time_scale({"scale": 1})
    assert behaviors._now() == pytest.approx(t1)  # no rewind, no jump
    wall.tick(5)
    assert behaviors._now() == pytest.approx(t1 + 5)


# --- the point of the feature: realistic durations, shrunk wall waits ---------


def test_scaled_mission_keeps_realistic_timestamps(client, wall):
    scaled = client.put("/_emulator/clock", json={"scale": 60}, headers=AUTH)
    assert scaled.json()["scale"] == 60
    mission = client.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    queued = client.post(
        "/api/v2.0.0/mission_queue",
        json={"mission_id": mission},
        headers={**AUTH, "X-AMR-Mission-Duration": "120"},
    ).json()
    wall.tick(3)  # 3 wall seconds = 180 simulated: 1 s lag + 120 s run

    entry = client.get(f"/api/v2.0.0/mission_queue/{queued['id']}", headers=AUTH).json()
    assert entry["state"] == "Done"
    # A 120 s mission reports 120 s of simulated execution, not 3.
    assert _iso_seconds(entry["started"], entry["finished"]) == 120


def test_battery_curve_follows_scaled_time(client, wall):
    client.put("/_emulator/clock", json={"scale": 60}, headers=AUTH)
    client.put(
        "/_emulator/battery",
        json={"percentage": 38, "charging": True, "charge_rate": 0.5, "target": 100},
        headers=AUTH,
    )
    wall.tick(1)  # 60 simulated seconds at 0.5 %/s -> +30 %
    pct = client.get("/api/v2.0.0/status", headers=AUTH).json()["battery_percentage"]
    assert pct == pytest.approx(68.0, abs=0.5)


# --- surface contract ----------------------------------------------------------


def test_get_reports_and_delete_restores_without_rewinding(client, wall):
    initial = client.get("/_emulator/clock", headers=AUTH)
    assert initial.json()["scale"] == 1.0
    client.put("/_emulator/clock", json={"scale": 30}, headers=AUTH)
    wall.tick(2)
    before = behaviors._now()
    doc = client.delete("/_emulator/clock", headers=AUTH).json()
    assert doc["scale"] == 1.0
    assert behaviors._now() >= before  # time never rewinds


@pytest.mark.parametrize(
    "body",
    [{}, {"scale": 0}, {"scale": -5}, {"scale": "fast"}, {"scale": True}, {"scale": 1e9}, []],
)
def test_invalid_scale_is_rejected_and_clock_untouched(client, body):
    response = client.put("/_emulator/clock", json=body, headers=AUTH)
    assert response.status_code == 400
    assert response.json()["error_human"]
    untouched = client.get("/_emulator/clock", headers=AUTH)
    assert untouched.json()["scale"] == 1.0


def test_clock_requires_auth(client):
    unauthenticated_read = client.get("/_emulator/clock")
    assert unauthenticated_read.status_code == 401
    unauthenticated_write = client.put("/_emulator/clock", json={"scale": 60})
    assert unauthenticated_write.status_code == 401


def test_index_documents_clock(client):
    assert "clock" in client.get("/").json()


def test_fleet_serves_the_same_clock_surface(wall):
    fleet = TestClient(create_fleet_app("1.5.0"))
    initial = fleet.get("/_emulator/clock", headers=KEY)
    assert initial.json()["scale"] == 1.0
    scaled = fleet.put("/_emulator/clock", json={"scale": 60}, headers=KEY)
    assert scaled.json()["scale"] == 60
    t0 = behaviors._now()
    wall.tick(1)
    assert behaviors._now() == pytest.approx(t0 + 60)  # embedded robots share it
    rejected = fleet.put("/_emulator/clock", json={"scale": 0}, headers=KEY)
    assert rejected.status_code == 400
    unauthenticated = fleet.get("/_emulator/clock")
    assert unauthenticated.status_code == 401
    assert "clock" in fleet.get("/", headers=KEY).json()


def test_cli_time_scale_flag_parses():
    from amr_emulator.cli import build_parser

    args = build_parser().parse_args(["--time-scale", "60"])
    assert args.time_scale == 60.0
    assert build_parser().parse_args([]).time_scale == 1.0
