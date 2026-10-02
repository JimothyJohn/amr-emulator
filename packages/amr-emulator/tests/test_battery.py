"""Battery control: /_emulator/battery sets the level and runs charging
curves, and /status, /metrics, and the fleet view all report the same
number. Time is frozen via behaviors._now, so every curve is exact."""

import pytest
from amr_emulator import behaviors
from amr_emulator.app import create_app
from amr_emulator.auth import expected_token
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
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


@pytest.fixture()
def robot():
    return TestClient(create_app("3.8.1"))


def put_battery(robot, body, headers=AUTH):
    return robot.put("/_emulator/battery", headers=headers, json=body)


def battery(robot, headers=AUTH):
    return robot.get("/_emulator/battery", headers=headers).json()


def status(robot, headers=AUTH):
    return robot.get("/api/v2.0.0/status", headers=headers).json()


def queue_mission(robot, headers=AUTH):
    guid = robot.get("/api/v2.0.0/missions", headers=headers).json()[0]["guid"]
    robot.post("/api/v2.0.0/mission_queue", headers=headers, json={"mission_id": guid})


def test_battery_surface_requires_auth(robot):
    responses = [
        robot.get("/_emulator/battery"),
        robot.put("/_emulator/battery", json={"percentage": 50}),
        robot.delete("/_emulator/battery"),
    ]
    assert [r.status_code for r in responses] == [401, 401, 401]


def test_untouched_surface_reports_the_stock_model(clock, robot):
    doc = battery(robot)
    assert doc["percentage"] == pytest.approx(behaviors.BATTERY_START)
    assert doc["charging"] is False
    assert doc["charge_rate"] == pytest.approx(behaviors.CHARGE_RATE_DEFAULT)
    assert doc["target"] == pytest.approx(behaviors.CHARGE_TARGET_DEFAULT)
    # Stock drain still applies: one mission (1s lag + 10s duration) drains
    # exactly DRAIN_PER_S * 10.
    queue_mission(robot)
    clock.tick(11.0)
    expected = behaviors.BATTERY_START - behaviors.BATTERY_DRAIN_PER_S * 10.0
    assert status(robot)["battery_percentage"] == pytest.approx(expected)
    assert battery(robot)["percentage"] == pytest.approx(expected)


def test_set_percentage_shows_up_everywhere(robot):
    response = put_battery(robot, {"percentage": 42.5})
    assert response.status_code == 200
    assert response.json()["percentage"] == pytest.approx(42.5)
    doc = status(robot)
    assert doc["battery_percentage"] == pytest.approx(42.5)
    assert doc["battery_time_remaining"] == int(42.5 * behaviors.BATTERY_SECONDS_PER_PERCENT)
    metrics = robot.get("/api/v2.0.0/metrics", headers=AUTH).text
    assert "mir_robot_battery_percent 42.5" in metrics


def test_charging_curve_climbs_and_caps_at_target(clock, robot):
    put_battery(robot, {"percentage": 80.0, "charging": True, "charge_rate": 1.0, "target": 95.0})
    clock.tick(10.0)
    assert status(robot)["battery_percentage"] == pytest.approx(90.0)
    clock.tick(10.0)  # 5 more percent to the target, then the curve stops
    assert status(robot)["battery_percentage"] == pytest.approx(95.0)
    clock.tick(600.0)
    doc = battery(robot)
    assert doc["percentage"] == pytest.approx(95.0), "never overshoots the target"
    assert doc["charging"] is True


def test_stopping_the_charge_freezes_the_level(clock, robot):
    put_battery(robot, {"percentage": 50.0, "charging": True, "charge_rate": 2.0})
    clock.tick(5.0)  # 50 + 10
    response = put_battery(robot, {"charging": False})
    assert response.json()["percentage"] == pytest.approx(60.0)
    clock.tick(600.0)  # idle robot: no drain, no charge
    assert status(robot)["battery_percentage"] == pytest.approx(60.0)


def test_drain_resumes_from_the_set_level(clock, robot):
    put_battery(robot, {"percentage": 50.0})
    queue_mission(robot)
    clock.tick(11.0)  # full mission: 10 executing seconds
    expected = 50.0 - behaviors.BATTERY_DRAIN_PER_S * 10.0
    assert status(robot)["battery_percentage"] == pytest.approx(expected)


def test_charging_beats_drain_while_a_mission_runs(clock, robot):
    put_battery(robot, {"percentage": 50.0, "charging": True, "charge_rate": 1.0})
    queue_mission(robot)
    clock.tick(11.0)  # 11s of charge (+11) vs 10 executing seconds (-0.5)
    assert status(robot)["battery_percentage"] == pytest.approx(50.0 + 11.0 - 0.5)


def test_pause_freezes_the_charging_curve(clock, robot):
    put_battery(robot, {"percentage": 50.0, "charging": True, "charge_rate": 1.0})
    clock.tick(5.0)
    robot.put("/api/v2.0.0/status", headers=AUTH, json={"state_id": 4})
    clock.tick(600.0)  # a paused robot's sim clock stands still
    assert status(robot)["battery_percentage"] == pytest.approx(55.0)
    robot.put("/api/v2.0.0/status", headers=AUTH, json={"state_id": 3})
    clock.tick(5.0)
    assert status(robot)["battery_percentage"] == pytest.approx(60.0)


def test_low_battery_floors_at_zero_not_the_stock_floor(clock, robot):
    # The stock model floors at BATTERY_FLOOR, but a user-set level below it
    # must stick — and drain from there stops at the set level's floor.
    put_battery(robot, {"percentage": 5.0})
    assert status(robot)["battery_percentage"] == pytest.approx(5.0)
    queue_mission(robot)
    clock.tick(11.0)
    assert status(robot)["battery_percentage"] == pytest.approx(5.0), (
        "drain never pulls the level below the anchored floor"
    )


def test_target_below_current_level_never_discharges(clock, robot):
    put_battery(robot, {"percentage": 98.0, "charging": True, "target": 95.0})
    clock.tick(600.0)
    assert battery(robot)["percentage"] == pytest.approx(98.0)


def test_delete_restores_the_stock_model(clock, robot):
    put_battery(robot, {"percentage": 10.0, "charging": True, "charge_rate": 9.0})
    cleared = robot.delete("/_emulator/battery", headers=AUTH)
    assert cleared.status_code == 200
    doc = cleared.json()
    assert doc["percentage"] == pytest.approx(behaviors.BATTERY_START)
    assert doc["charging"] is False
    assert status(robot)["battery_percentage"] == pytest.approx(behaviors.BATTERY_START)


def test_battery_critical_fault_wins_over_the_surface(robot):
    put_battery(robot, {"percentage": 95.0})
    robot.put("/_emulator/faults", headers=AUTH, json={"faults": ["battery_critical"]})
    assert status(robot)["battery_percentage"] == pytest.approx(1.5)
    assert battery(robot)["percentage"] == pytest.approx(1.5)
    robot.delete("/_emulator/faults", headers=AUTH)
    assert status(robot)["battery_percentage"] == pytest.approx(95.0)


def test_malformed_bodies_are_400(robot):
    for body in (
        {},
        [],
        "50",
        {"percentage": -1},
        {"percentage": 101},
        {"percentage": "high"},
        {"percentage": True},
        {"charging": "yes"},
        {"charge_rate": 0},
        {"charge_rate": -2},
        {"charge_rate": 101},
        {"charge_rate": False},
        {"target": 100.5},
        {"charging_rate": 1.0},  # typo'd key must not pass silently
        {"percentage": 50, "warp": 9},
    ):
        response = robot.put("/_emulator/battery", headers=AUTH, json=body)
        assert response.status_code == 400, body
    # Nothing above may have leaked into the model.
    assert battery(robot)["percentage"] == pytest.approx(behaviors.BATTERY_START)


def test_battery_is_session_isolated(clock, robot):
    session = {**AUTH, "X-AMR-Session": "charger-bay"}
    put_battery(robot, {"percentage": 30.0, "charging": True, "charge_rate": 1.0}, headers=session)
    clock.tick(10.0)
    assert status(robot, headers=session)["battery_percentage"] == pytest.approx(40.0)
    assert status(robot)["battery_percentage"] == pytest.approx(behaviors.BATTERY_START)
    assert battery(robot)["charging"] is False, "default robot untouched"


def test_fleet_reports_the_charged_level(clock):
    app = create_fleet_app("1.5.0")
    fleet = TestClient(app)
    robot = TestClient(app.state.emulator.robots[0].app)
    put_battery(robot, {"percentage": 60.0, "charging": True, "charge_rate": 1.0})
    clock.tick(20.0)
    robots = fleet.get("/api/v1/robots", headers=KEY).json()["robots"]
    detail = fleet.get(f"/api/v1/robots/{robots[0]['robot-id']}", headers=KEY).json()
    assert detail["runtime-data"]["battery-percentage"] == pytest.approx(80.0)
    other = fleet.get(f"/api/v1/robots/{robots[1]['robot-id']}", headers=KEY).json()
    assert other["runtime-data"]["battery-percentage"] == pytest.approx(behaviors.BATTERY_START)


def test_charge_to_target_then_drain_end_to_end(clock, robot):
    """The scenario the surface exists for: charge to 95%, then work."""
    put_battery(robot, {"percentage": 80.0, "charging": True, "charge_rate": 1.5, "target": 95.0})
    clock.tick(10.0)  # 80 + 15 capped at 95
    assert status(robot)["battery_percentage"] == pytest.approx(95.0)
    put_battery(robot, {"charging": False})
    queue_mission(robot)
    clock.tick(11.0)
    expected = 95.0 - behaviors.BATTERY_DRAIN_PER_S * 10.0
    assert status(robot)["battery_percentage"] == pytest.approx(expected)
