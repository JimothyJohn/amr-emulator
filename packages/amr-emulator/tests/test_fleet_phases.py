"""Richer fleet order phases, pinned by the official Fleet 1.5.0 OpenAPI:

- ``phases[].fallback-mission-id`` — when the primary mission aborts, the
  fleet dispatches the fallback on the same robot and the order's lifecycle
  continues; ``DELETE /serial-order/fallback/{serialOrderId}`` (202 {id})
  aborts a running fallback.
- ``serial-order.priority`` is the spec enum {Low, Medium, High}; High
  preempts robot selection (shortest live queue) instead of round-robin.
- ``POST/DELETE /api/v1/system/evacuation`` — evacuation aborts every
  robot's queue and rejects new serial orders until terminated.

Deterministic: frozen sim clock, stepped manually.
"""

import pytest
from amr_emulator import behaviors
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
from starlette.testclient import TestClient

KEY = {"x-api-key": DEFAULT_API_KEY}
T0 = 1_750_000_000.0


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
def fleet(clock):
    return TestClient(create_fleet_app("1.5.0", mission_duration=10.0))


def robots(fleet):
    return [r["robot-id"] for r in fleet.get("/api/v1/robots", headers=KEY).json()["robots"]]


def site_mission(fleet):
    return fleet.get("/api/v1/site/mission", headers=KEY).json()["missions"][0]["id"]


def post_order(fleet, mission, *, robot_id=None, priority="Medium", fallback=None):
    phase = {"mission-id": mission}
    if fallback is not None:
        phase["fallback-mission-id"] = fallback
    body = {"serial-order": {"priority": priority, "phases": [phase]}}
    if robot_id:
        body["serial-order"]["robot-id"] = robot_id
    return fleet.post("/api/v1/serial-order", json=body, headers=KEY)


def order_status(fleet, serial_id):
    orders = fleet.get("/api/v1/order", headers=KEY).json()
    mine = [o for o in orders if o["order-id"]]
    # orders carry no serial id in the flat view; match via serial-order detail
    detail = fleet.get(f"/api/v1/serial-order/{serial_id}", headers=KEY).json()
    ids = {p["order-id"] for p in detail["phases"]}
    return [o["order-status"] for o in mine if o["order-id"] in ids]


def abort_robot_queue(fleet, robot_id):
    """mission_failure via the chaos proxy aborts the robot's queue."""
    r = fleet.put(
        f"/_emulator/robots/{robot_id}/faults", json={"faults": ["mission_failure"]}, headers=KEY
    )
    assert r.status_code == 200
    fleet.delete(f"/_emulator/robots/{robot_id}/faults", headers=KEY)


# --- fallback missions ----------------------------------------------------------


def test_aborted_primary_dispatches_the_fallback_and_the_order_recovers(fleet, clock):
    mission = site_mission(fleet)
    r1 = robots(fleet)[0]
    serial = post_order(fleet, mission, robot_id=r1, fallback=mission).json()["id"]
    clock.tick(2)  # primary Executing
    abort_robot_queue(fleet, r1)
    # the read model reconciles: aborted primary -> fallback dispatched
    (status,) = order_status(fleet, serial)
    assert status in ("Pending", "Executing")
    clock.tick(15)  # fallback runs to completion
    (status,) = order_status(fleet, serial)
    assert status == "Finished"


def test_order_without_fallback_just_aborts(fleet, clock):
    mission = site_mission(fleet)
    r1 = robots(fleet)[0]
    serial = post_order(fleet, mission, robot_id=r1).json()["id"]
    clock.tick(2)
    abort_robot_queue(fleet, r1)
    (status,) = order_status(fleet, serial)
    assert status == "Aborted"


def test_unknown_fallback_mission_is_rejected_atomically(fleet, clock):
    mission = site_mission(fleet)
    r1 = robots(fleet)[0]
    response = post_order(fleet, mission, robot_id=r1, fallback="not-a-mission")
    assert response.status_code == 400
    orders = fleet.get("/api/v1/order", headers=KEY)
    assert orders.json() == []


def test_delete_fallback_aborts_a_running_fallback(fleet, clock):
    mission = site_mission(fleet)
    r1 = robots(fleet)[0]
    serial = post_order(fleet, mission, robot_id=r1, fallback=mission).json()["id"]
    clock.tick(2)
    abort_robot_queue(fleet, r1)
    (status,) = order_status(fleet, serial)  # reconciliation dispatches fallback
    assert status in ("Pending", "Executing")
    response = fleet.delete(f"/api/v1/serial-order/fallback/{serial}", headers=KEY)
    assert response.status_code == 202
    assert response.json() == {"id": serial}
    (status,) = order_status(fleet, serial)
    assert status == "Aborted"


def test_delete_fallback_without_a_running_fallback_is_a_400(fleet, clock):
    mission = site_mission(fleet)
    serial = post_order(fleet, mission).json()["id"]
    no_fallback = fleet.delete(f"/api/v1/serial-order/fallback/{serial}", headers=KEY)
    assert no_fallback.status_code == 400
    unknown = fleet.delete("/api/v1/serial-order/fallback/nope", headers=KEY)
    assert unknown.status_code == 404


# --- priority -------------------------------------------------------------------


def test_priority_must_be_the_spec_enum(fleet):
    # enforced by request-body validation against the official schema
    response = post_order(fleet, site_mission(fleet), priority="Urgent")
    assert response.status_code == 400
    assert "'Low', 'Medium', 'High'" in response.json()["error_human"]


def test_high_priority_takes_the_least_loaded_robot(fleet, clock):
    mission = site_mission(fleet)
    r1, r2 = robots(fleet)
    # Load r1 with two queued missions; r2 idle. Frozen clock: nothing drains.
    post_order(fleet, mission, robot_id=r1)
    post_order(fleet, mission, robot_id=r1)
    serial = post_order(fleet, mission, priority="High").json()["id"]
    detail = fleet.get(f"/api/v1/serial-order/{serial}", headers=KEY).json()
    assert detail["robot-id"] == r2  # preempts rotation, shortest queue wins


def test_medium_priority_keeps_round_robin(fleet, clock):
    mission = site_mission(fleet)
    r1, r2 = robots(fleet)
    post_order(fleet, mission, robot_id=r1)
    post_order(fleet, mission, robot_id=r1)
    first = post_order(fleet, mission).json()["id"]
    second = post_order(fleet, mission).json()["id"]
    picked = {
        fleet.get(f"/api/v1/serial-order/{s}", headers=KEY).json()["robot-id"]
        for s in (first, second)
    }
    assert picked == {r1, r2}  # fair rotation, load-blind


# --- evacuation -----------------------------------------------------------------


def test_evacuation_aborts_everything_and_gates_new_orders(fleet, clock):
    mission = site_mission(fleet)
    serial = post_order(fleet, mission).json()["id"]
    clock.tick(2)
    evacuated = fleet.post("/api/v1/system/evacuation", headers=KEY)
    assert evacuated.status_code == 201
    (status,) = order_status(fleet, serial)
    assert status == "Aborted"
    rejected = post_order(fleet, mission)
    assert rejected.status_code == 400
    assert "vacuation" in rejected.json()["error_human"]
    terminated = fleet.delete("/api/v1/system/evacuation", headers=KEY)
    assert terminated.status_code == 200
    accepted = post_order(fleet, mission)
    assert accepted.status_code == 201


def test_evacuation_suppresses_fallback_dispatch(fleet, clock):
    mission = site_mission(fleet)
    r1 = robots(fleet)[0]
    serial = post_order(fleet, mission, robot_id=r1, fallback=mission).json()["id"]
    clock.tick(2)
    evacuated = fleet.post("/api/v1/system/evacuation", headers=KEY)
    assert evacuated.status_code == 201
    (status,) = order_status(fleet, serial)
    assert status == "Aborted"  # no fallback resurrection during an evacuation
    fleet.delete("/api/v1/system/evacuation", headers=KEY)
