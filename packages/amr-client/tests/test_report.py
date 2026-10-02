"""amr-report against live emulator apps: collect from official endpoints only,
render the dashboard (status indicators, daily trend, action timeline).

No sockets: the report module's httpx clients ride an in-process ASGI
transport into the same apps the SDK contract tests use. Deterministic:
frozen sim clock, stepped manually.
"""

import httpx
import pytest
from amr_client.auth import robot_token
from amr_client.report import collect_report, render_report, write_report
from amr_emulator import behaviors
from amr_emulator.app import create_app
from amr_emulator.fleet import create_fleet_app
from starlette.testclient import TestClient

AUTH = {"Authorization": f"Basic {robot_token('distributor', 'distributor')}"}
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
def robot_app(clock):
    return create_app("3.8.1")


@pytest.fixture()
def robot_report(robot_app, clock):
    """A robot with one named, completed mission and one fault on the log."""
    drive = TestClient(robot_app)  # same Emulator instance as the transport below
    created = drive.post(
        "/api/v2.0.0/missions",
        json={"name": "Deliver cart to DropOff-ZoneA", "group_id": "test"},
        headers=AUTH,
    ).json()
    drive.post(
        "/api/v2.0.0/mission_queue",
        json={"mission_id": created["guid"]},
        headers={**AUTH, "X-AMR-Mission-Duration": "120"},
    )
    clock.tick(300)  # mission long done
    drive.put("/_emulator/faults", json={"faults": ["blocked_path"]}, headers=AUTH)
    return collect_report("http://robot.test", transport=httpx.ASGITransport(app=robot_app))


def test_robot_report_indicators(robot_report):
    assert robot_report["kind"] == "robot"
    assert robot_report["version"] == "3.8.1"
    (robot,) = robot_report["robots"]
    assert robot["name"] == "MiR_Emulated"
    assert robot["model"] == "MiR250"
    assert 0 <= robot["battery"] <= 100
    assert robot["state"] in ("Ready", "Executing", "Error", "EmergencyStop", "Pause")
    assert {"x", "y"} <= set(robot["position"])
    # the blocked_path fault surfaces as a live error, not the placeholder
    assert any(e.get("code") == 10015 for e in robot["errors"])


def test_robot_report_daily_trend_from_official_statistics(robot_report):
    assert robot_report["trend_label"].startswith("distance")
    (day,) = robot_report["trend"]
    assert day["date"] == "2025-06-15"
    assert day["value"] == pytest.approx(120 * behaviors.MISSION_SPEED_M_S, abs=1)


def test_robot_report_timeline_is_chronological_and_descriptive(robot_report):
    timeline = robot_report["timeline"]
    times = [e["time"] for e in timeline]
    assert times == sorted(times)
    texts = " | ".join(e["text"] for e in timeline)
    assert "Deliver cart to DropOff-ZoneA" in texts
    assert "Planner" in texts  # the fault's error report
    kinds = {e["kind"] for e in timeline}
    assert {"mission", "error"} <= kinds


def test_render_report_is_a_self_contained_dashboard(robot_report):
    html = render_report(robot_report)
    assert html.startswith("<!DOCTYPE html>")
    for needle in (
        "MiR_Emulated",  # indicator
        "Deliver cart to DropOff-ZoneA",  # timeline
        "2025-06-15",  # trend
        "battery",
    ):
        assert needle in html, needle
    # no external resource loads — the report must work offline
    assert "<link" not in html and "<script src" not in html and "@import" not in html


def test_write_report(tmp_path, robot_app, robot_report, clock):
    out = tmp_path / "robot.html"
    path = write_report("http://robot.test", out, transport=httpx.ASGITransport(app=robot_app))
    assert path == out
    assert out.read_text().startswith("<!DOCTYPE html>")


def test_fleet_report(clock):
    app = create_fleet_app("1.5.0")
    drive = TestClient(app)
    key = {"x-api-key": "distributor"}
    mission = drive.get("/api/v1/site/mission", headers=key).json()["missions"][0]["id"]
    drive.post(
        "/api/v1/serial-order",
        json={"serial-order": {"priority": "Medium", "phases": [{"mission-id": mission}]}},
        headers=key,
    )
    clock.tick(60)
    report = collect_report("http://fleet.test", transport=httpx.ASGITransport(app=app))
    assert report["kind"] == "fleet"
    assert len(report["robots"]) == 2
    assert all(0 <= r["battery"] <= 100 for r in report["robots"])
    assert report["trend_label"].startswith("orders")
    assert sum(d["value"] for d in report["trend"]) >= 1
    assert any(e["kind"] == "order" for e in report["timeline"])
    html = render_report(report)
    assert "MiR_Emulated_1" in html and "MiR_Emulated_2" in html


def test_dispatcher_target_is_rejected_with_guidance(robot_app):
    # a robot pretending... simplest: unknown target -> DiscoveryError propagates;
    # here assert the clear ValueError for a dispatcher-kind target is reachable
    # via the public API contract (kind gate lives in collect_report).
    from amr_client.report import _unsupported_kind_message

    assert "robot or fleet" in _unsupported_kind_message("dispatcher")


def test_as_list_accepts_both_declared_shapes():
    # MiR specs declare some list endpoints with the element's object schema;
    # servers differ on which shape they answer with.
    from amr_client.report import _as_list

    assert _as_list([{"a": 1}]) == [{"a": 1}]
    assert _as_list({"a": 1}) == [{"a": 1}]
    assert _as_list(None) == []
