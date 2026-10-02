"""Fault injection: /_emulator/faults drives the robot into the states
integrators must handle, and the whole stack — status, simulation, fleet
view — reflects them consistently. Time is frozen via behaviors._now."""

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


def set_faults(robot, faults, headers=AUTH):
    return robot.put("/_emulator/faults", headers=headers, json={"faults": faults})


def status(robot, headers=AUTH):
    return robot.get("/api/v2.0.0/status", headers=headers).json()


def test_fault_surface_requires_auth(robot):
    assert robot.get("/_emulator/faults").status_code == 401
    assert robot.put("/_emulator/faults", json={"faults": []}).status_code == 401


def test_catalog_lists_every_fault(robot):
    doc = robot.get("/_emulator/faults", headers=AUTH).json()
    assert doc["active"] == []
    assert set(doc["available"]) == {
        "emergency_stop",
        "error",
        "localization_lost",
        "battery_critical",
        "blocked_path",
        "mission_failure",
        "connection_drop",
    }


def test_emergency_stop_flips_status_and_clears_on_delete(robot):
    response = set_faults(robot, ["emergency_stop"])
    assert response.status_code == 200
    assert response.json()["active"] == ["emergency_stop"]

    doc = status(robot)
    assert doc["state_id"] == 10
    assert doc["state_text"] == "EmergencyStop"
    assert any(e["module"] == "SafetySystem" for e in doc["errors"])
    assert doc["velocity"] == {"linear": 0.0, "angular": 0.0}

    cleared = robot.delete("/_emulator/faults", headers=AUTH)
    assert cleared.status_code == 200 and cleared.json()["active"] == []
    doc = status(robot)
    assert doc["state_id"] == 3 and doc["state_text"] == "Ready"
    assert all(e["module"] == "emulated" for e in doc["errors"])


def test_emergency_stop_freezes_an_executing_mission(clock, robot):
    mission = robot.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)  # executing (1s lag + 10s duration)
    assert status(robot)["state_text"] == "Executing"

    set_faults(robot, ["emergency_stop"])
    clock.tick(60.0)  # a real minute passes while e-stopped
    queue = robot.get("/api/v2.0.0/mission_queue", headers=AUTH).json()
    assert queue[0]["state"] == "Executing", "mission must not finish during e-stop"

    robot.delete("/_emulator/faults", headers=AUTH)
    clock.tick(8.5)  # remaining ~9s of execution < wait
    assert status(robot)["state_text"] == "Executing"
    clock.tick(1.0)
    queue = robot.get("/api/v2.0.0/mission_queue", headers=AUTH).json()
    assert queue[0]["state"] == "Done", "mission resumes exactly where it froze"


def test_error_faults_clear_via_documented_clear_error(robot):
    set_faults(robot, ["localization_lost"])
    doc = status(robot)
    assert doc["state_id"] == 12
    assert any(e["module"] == "Localization" for e in doc["errors"])

    put = robot.put("/api/v2.0.0/status", headers=AUTH, json={"clear_error": True})
    assert put.status_code == 200
    assert robot.get("/_emulator/faults", headers=AUTH).json()["active"] == []
    assert status(robot)["state_id"] == 3


def test_clear_error_does_not_release_an_emergency_stop(robot):
    set_faults(robot, ["emergency_stop", "error"])
    robot.put("/api/v2.0.0/status", headers=AUTH, json={"clear_error": True})
    doc = robot.get("/_emulator/faults", headers=AUTH).json()
    assert doc["active"] == ["emergency_stop"]
    assert status(robot)["state_id"] == 10


def test_battery_critical_changes_battery_not_state(robot):
    set_faults(robot, ["battery_critical"])
    doc = status(robot)
    assert doc["battery_percentage"] == pytest.approx(1.5)
    assert doc["state_id"] == 3
    assert any(e["module"] == "Battery" for e in doc["errors"])


def test_blocked_path_reports_planner_error_while_executing(clock, robot):
    mission = robot.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)
    set_faults(robot, ["blocked_path"])
    doc = status(robot)
    assert doc["state_text"] == "Executing", "robot keeps trying while the path is blocked"
    assert any(e["module"] == "Planner" for e in doc["errors"])


def test_blocked_path_is_not_a_holding_fault(clock, robot):
    # Deliberate design (see scenarios/novo_nordisk_crowded_route.py): a real
    # MiR replans around an obstruction, so blocked_path must NOT freeze the
    # mission simulation the way an e-stop does.
    mission = robot.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)
    set_faults(robot, ["blocked_path"])
    clock.tick(9.5)  # past the 1s lag + 10s duration
    queue = robot.get("/api/v2.0.0/mission_queue", headers=AUTH).json()
    assert queue[0]["state"] == "Done", "the mission completes despite the blocked path"
    assert any(e["module"] == "Planner" for e in status(robot)["errors"])


def test_cause_faults_survive_clear_error_and_say_so(robot):
    # blocked_path and battery_critical model a physical cause; an error
    # reset cannot remove it, and the error document must not promise
    # otherwise: non_resettable is true, and only /_emulator/faults clears.
    set_faults(robot, ["blocked_path", "battery_critical"])
    for error in status(robot)["errors"]:
        assert error["non_resettable"] is True, error

    robot.put("/api/v2.0.0/status", headers=AUTH, json={"clear_error": True})
    active = robot.get("/_emulator/faults", headers=AUTH).json()["active"]
    assert set(active) == {"blocked_path", "battery_critical"}
    modules = {e["module"] for e in status(robot)["errors"]}
    assert modules == {"Planner", "Battery"}, "the errors come right back"

    robot.delete("/_emulator/faults", headers=AUTH)
    assert robot.get("/_emulator/faults", headers=AUTH).json()["active"] == []
    assert status(robot)["battery_percentage"] > 1.5


def test_unknown_and_malformed_fault_requests_are_400(robot):
    bad = set_faults(robot, ["warp_core_breach"])
    assert bad.status_code == 400
    assert "available" in bad.json()["error_human"]
    for body in ({}, {"faults": "emergency_stop"}, {"faults": [1]}, []):
        response = robot.put("/_emulator/faults", headers=AUTH, json=body)
        assert response.status_code == 400, body


def test_faults_are_session_isolated(robot):
    session = {**AUTH, "X-AMR-Session": "crew-a"}
    set_faults(robot, ["emergency_stop"], headers=session)
    assert status(robot, headers=session)["state_id"] == 10
    assert status(robot)["state_id"] == 3, "default robot unaffected"
    assert robot.get("/_emulator/faults", headers=AUTH).json()["active"] == []


def test_fleet_sees_the_robots_fault_as_official_end_state():
    app = create_fleet_app("1.5.0")
    fleet = TestClient(app)
    robot = TestClient(app.state.emulator.robots[0].app)
    set_faults(robot, ["emergency_stop"])

    robots = fleet.get("/api/v1/robots", headers=KEY).json()["robots"]
    detail = fleet.get(f"/api/v1/robots/{robots[0]['robot-id']}", headers=KEY).json()
    assert detail["robot-end-state"] == "Emergency Stop"  # official fleet enum value
    assert any(e["module"] == "SafetySystem" for e in detail["errors"])

    other = fleet.get(f"/api/v1/robots/{robots[1]['robot-id']}", headers=KEY).json()
    assert other["robot-end-state"] == "Idle"


def test_mission_failure_aborts_running_and_pending_missions(clock, robot):
    mission = robot.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    for _ in range(2):
        robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)  # first executing, second pending

    set_faults(robot, ["mission_failure"])
    doc = status(robot)
    assert doc["state_id"] == 12
    assert any(e["module"] == "MissionController" for e in doc["errors"])
    queue = robot.get("/api/v2.0.0/mission_queue", headers=AUTH).json()
    assert [entry["state"] for entry in queue] == ["Aborted", "Aborted"]

    # clear_error releases the fault, but aborted missions stay aborted
    robot.put("/api/v2.0.0/status", headers=AUTH, json={"clear_error": True})
    assert status(robot)["state_id"] == 3
    queue = robot.get("/api/v2.0.0/mission_queue", headers=AUTH).json()
    assert [entry["state"] for entry in queue] == ["Aborted", "Aborted"]


def test_mission_failure_spares_already_finished_missions(clock, robot):
    mission = robot.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(12.0)  # ran to completion (1s lag + 10s)
    robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)  # second executing

    set_faults(robot, ["mission_failure"])
    states = [e["state"] for e in robot.get("/api/v2.0.0/mission_queue", headers=AUTH).json()]
    assert states == ["Done", "Aborted"]


def test_robot_is_free_after_an_abort(clock, robot):
    mission = robot.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)
    set_faults(robot, ["mission_failure"])
    robot.put("/api/v2.0.0/status", headers=AUTH, json={"clear_error": True})

    # A fresh mission after the abort runs normally from "now".
    robot.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)
    queue = robot.get("/api/v2.0.0/mission_queue", headers=AUTH).json()
    assert [entry["state"] for entry in queue] == ["Aborted", "Executing"]
    assert status(robot)["state_text"] == "Executing"


def test_fleet_reports_aborted_orders_after_mission_failure(clock):
    app = create_fleet_app("1.5.0")
    fleet = TestClient(app)
    robot = TestClient(app.state.emulator.robots[0].app)
    robots = fleet.get("/api/v1/robots", headers=KEY).json()["robots"]
    mission = fleet.get("/api/v1/site/mission", headers=KEY).json()["missions"][0]["id"]
    fleet.post(
        "/api/v1/serial-order",
        headers=KEY,
        json={
            "serial-order": {"robot-id": robots[0]["robot-id"], "phases": [{"mission-id": mission}]}
        },
    )
    clock.tick(2.0)
    set_faults(robot, ["mission_failure"])
    order = fleet.get("/api/v1/order", headers=KEY).json()[0]
    assert order["order-status"] == "Aborted"
    detail = fleet.get(f"/api/v1/robots/{robots[0]['robot-id']}", headers=KEY).json()
    assert detail["robot-end-state"] == "Error"
