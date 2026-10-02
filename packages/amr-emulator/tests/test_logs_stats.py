"""Official log & statistics surfaces answer with sim-derived truth.

GET /log/error_reports accumulates a spec-shaped report per fault
activation (session-isolated, surviving the fault being cleared);
GET /statistics/distance reports per-day driven distance derived from the
mission timeline. Deterministic: frozen clock, stepped manually.
"""

import pytest
from amr_emulator import behaviors
from amr_emulator.app import create_app
from amr_emulator.auth import expected_token
from starlette.testclient import TestClient

AUTH = {"Authorization": f"Basic {expected_token('distributor', 'distributor')}"}
T0 = 1_750_000_000.0  # 2025-06-15T15:06:40Z


class Clock:
    def __init__(self, start: float = T0) -> None:
        self.now = start

    def tick(self, seconds: float) -> None:
        self.now += seconds

    def __call__(self) -> float:
        return self.now


@pytest.fixture()
def clock(monkeypatch):
    c = Clock()
    monkeypatch.setattr(behaviors, "_now", c)
    return c


@pytest.fixture()
def client(clock):
    return TestClient(create_app("3.8.1"))


def reports(client, **headers):
    return client.get("/api/v2.0.0/log/error_reports", headers={**AUTH, **headers}).json()


# --- error reports from faults -------------------------------------------------


def test_fault_activation_appends_a_spec_shaped_error_report(client, clock):
    before = {r["id"] for r in reports(client)}
    client.put("/_emulator/faults", json={"faults": ["emergency_stop"]}, headers=AUTH)
    fresh = [r for r in reports(client) if r["id"] not in before]
    assert len(fresh) == 1
    report = fresh[0]
    assert report["module"] == "SafetySystem"
    assert "Emergency stop" in report["description"]
    assert report["time"] == "2025-06-15T15:06:40"
    assert set(report) <= {
        "id",
        "time",
        "description",
        "module",
        "generating",
        "ready",
        "download_url",
    }


def test_reports_survive_fault_clearing_and_accumulate(client, clock):
    client.put("/_emulator/faults", json={"faults": ["emergency_stop"]}, headers=AUTH)
    client.delete("/_emulator/faults", headers=AUTH)
    clock.tick(60)
    client.put("/_emulator/faults", json={"faults": ["blocked_path"]}, headers=AUTH)
    modules = [r["module"] for r in reports(client)]
    assert "SafetySystem" in modules and "Planner" in modules


def test_reactivating_the_same_fault_does_not_duplicate_while_active(client, clock):
    client.put("/_emulator/faults", json={"faults": ["error"]}, headers=AUTH)
    n = len(reports(client))
    client.put("/_emulator/faults", json={"faults": ["error"]}, headers=AUTH)  # no-op
    assert len(reports(client)) == n


def test_error_reports_are_session_isolated(client, clock):
    client.put(
        "/_emulator/faults",
        json={"faults": ["emergency_stop"]},
        headers={**AUTH, "X-AMR-Session": "cell-a"},
    )
    a = reports(client, **{"X-AMR-Session": "cell-a"})
    b = reports(client, **{"X-AMR-Session": "cell-b"})
    assert any(r["module"] == "SafetySystem" for r in a)
    assert not any(r["module"] == "SafetySystem" for r in b)


# --- daily distance from the mission timeline -----------------------------------


def enqueue(client, duration: float) -> int:
    mission = client.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    return client.post(
        "/api/v2.0.0/mission_queue",
        json={"mission_id": mission},
        headers={**AUTH, "X-AMR-Mission-Duration": str(duration)},
    ).json()["id"]


def distance(client):
    return client.get("/api/v2.0.0/statistics/distance", headers=AUTH).json()


def test_distance_is_zero_for_today_before_any_mission(client, clock):
    doc = distance(client)
    assert doc == [{"date": "2025-06-15T00:00:00", "distance": 0.0}]


def test_distance_accumulates_executed_seconds_times_speed(client, clock):
    enqueue(client, 100)
    clock.tick(200)  # 1 s pending lag + 100 s run, long done
    doc = distance(client)
    assert doc == [
        {"date": "2025-06-15T00:00:00", "distance": round(100 * behaviors.MISSION_SPEED_M_S, 2)}
    ]
    enqueue(client, 60)
    clock.tick(120)
    assert distance(client)[0]["distance"] == round(160 * behaviors.MISSION_SPEED_M_S, 2)


def test_distance_counts_only_elapsed_execution(client, clock):
    enqueue(client, 100)
    clock.tick(51)  # 1 s lag + 50 s of the 100 s mission
    assert distance(client)[0]["distance"] == pytest.approx(
        50 * behaviors.MISSION_SPEED_M_S, abs=0.5
    )


def test_distance_splits_across_sim_days(client, clock):
    # 2025-06-15T15:06:40 + 8.9 h ≈ midnight; run a mission spanning it
    clock.tick(31_900)  # -> 23:58:20
    enqueue(client, 400)  # crosses 00:00
    clock.tick(500)
    doc = distance(client)
    assert [d["date"] for d in doc] == ["2025-06-15T00:00:00", "2025-06-16T00:00:00"]
    total = sum(d["distance"] for d in doc)
    assert total == pytest.approx(400 * behaviors.MISSION_SPEED_M_S, abs=0.5)
    assert all(d["distance"] > 0 for d in doc)
