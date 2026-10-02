"""Fleet chaos proxy: /_emulator/robots/{robot-id}/{faults|battery} reaches
an embedded robot's emulator-only surfaces through the fleet's HTTP port —
no in-process access required. Everything here talks to the FLEET client
only, which is the point: a fleet integration must be able to e-stop or
drain a robot mid-order from outside."""

import pytest
from amr_emulator import behaviors
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
from starlette.testclient import TestClient

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
def fleet():
    return TestClient(create_fleet_app("1.5.0"))


def robot_ids(fleet):
    return [r["robot-id"] for r in fleet.get("/api/v1/robots", headers=KEY).json()["robots"]]


def robot_detail(fleet, rid):
    return fleet.get(f"/api/v1/robots/{rid}", headers=KEY).json()


def test_proxy_requires_fleet_auth(fleet):
    rid = robot_ids(fleet)[0]
    responses = [
        fleet.get(f"/_emulator/robots/{rid}/faults"),
        fleet.put(f"/_emulator/robots/{rid}/battery", json={"percentage": 50}),
    ]
    assert [r.status_code for r in responses] == [401, 401]


def test_unknown_robot_and_surface_are_404(fleet):
    rid = robot_ids(fleet)[0]
    assert fleet.get("/_emulator/robots/no-such-robot/faults", headers=KEY).status_code == 404
    for surface in ("recorder", "diff", "status"):
        response = fleet.get(f"/_emulator/robots/{rid}/{surface}", headers=KEY)
        assert response.status_code == 404, f"{surface} must not be proxied"


def test_estop_via_proxy_shows_in_the_fleet_view(fleet):
    first, second = robot_ids(fleet)[:2]
    response = fleet.put(
        f"/_emulator/robots/{first}/faults", headers=KEY, json={"faults": ["emergency_stop"]}
    )
    assert response.status_code == 200
    assert response.json()["active"] == ["emergency_stop"]

    assert robot_detail(fleet, first)["robot-end-state"] == "Emergency Stop"
    assert robot_detail(fleet, second)["robot-end-state"] == "Idle", "only the target robot"

    cleared = fleet.delete(f"/_emulator/robots/{first}/faults", headers=KEY)
    assert cleared.status_code == 200 and cleared.json()["active"] == []
    assert robot_detail(fleet, first)["robot-end-state"] == "Idle"


def test_battery_via_proxy_shows_in_runtime_data(clock, fleet):
    rid = robot_ids(fleet)[0]
    response = fleet.put(
        f"/_emulator/robots/{rid}/battery",
        headers=KEY,
        json={"percentage": 55.0, "charging": True, "charge_rate": 1.0, "target": 65.0},
    )
    assert response.status_code == 200
    clock.tick(20.0)  # 10 to the 65% cap, then it holds
    assert robot_detail(fleet, rid)["runtime-data"]["battery-percentage"] == pytest.approx(65.0)
    doc = fleet.get(f"/_emulator/robots/{rid}/battery", headers=KEY).json()
    assert doc["percentage"] == pytest.approx(65.0)
    assert doc["charging"] is True


def test_robot_validation_errors_pass_through(fleet):
    rid = robot_ids(fleet)[0]
    bad_fault = fleet.put(
        f"/_emulator/robots/{rid}/faults", headers=KEY, json={"faults": ["warp_core_breach"]}
    )
    assert bad_fault.status_code == 400
    assert "available" in bad_fault.json()["error_human"]
    bad_battery = fleet.put(
        f"/_emulator/robots/{rid}/battery", headers=KEY, json={"percentage": 101}
    )
    assert bad_battery.status_code == 400
    assert "percentage" in bad_battery.json()["error_human"]


def test_proxy_is_session_isolated(fleet):
    rid = robot_ids(fleet)[0]
    session = {**KEY, "X-AMR-Session": "chaos-crew"}
    fleet.put(
        f"/_emulator/robots/{rid}/faults", headers=session, json={"faults": ["emergency_stop"]}
    )
    detail = fleet.get(f"/api/v1/robots/{rid}", headers=session).json()
    assert detail["robot-end-state"] == "Emergency Stop"
    assert robot_detail(fleet, rid)["robot-end-state"] == "Idle", "default fleet untouched"


def test_estop_mid_order_holds_it_and_release_finishes_it(clock, fleet):
    """The DHL case: chaos-test an order in flight, fleet API only."""
    rid = robot_ids(fleet)[0]
    mission = fleet.get("/api/v1/site/mission", headers=KEY).json()["missions"][0]["id"]
    order = fleet.post(
        "/api/v1/serial-order",
        headers=KEY,
        json={"serial-order": {"robot-id": rid, "phases": [{"mission-id": mission}]}},
    )
    assert order.status_code == 201
    clock.tick(2.0)  # executing (1s pickup lag, 10s duration)
    assert fleet.get("/api/v1/order", headers=KEY).json()[0]["order-status"] == "Executing"

    fleet.put(f"/_emulator/robots/{rid}/faults", headers=KEY, json={"faults": ["emergency_stop"]})
    clock.tick(300.0)  # five minutes on the e-stop: the order must not finish
    assert fleet.get("/api/v1/order", headers=KEY).json()[0]["order-status"] == "Executing"
    assert robot_detail(fleet, rid)["robot-end-state"] == "Emergency Stop"

    fleet.delete(f"/_emulator/robots/{rid}/faults", headers=KEY)
    clock.tick(9.5)  # the remaining ~9s of execution resume in place
    assert fleet.get("/api/v1/order", headers=KEY).json()[0]["order-status"] == "Finished"


def test_fleet_treats_a_connection_dropped_robot_as_unreachable(fleet):
    """connection_drop on an embedded robot must not 500 the fleet — the
    fleet sees an unreachable robot, exactly like a rebooting one."""
    robot_id = robot_ids(fleet)[0]
    armed = fleet.put(
        f"/_emulator/robots/{robot_id}/faults",
        json={"faults": ["connection_drop"]},
        headers=KEY,
    )
    assert armed.status_code == 200
    listing = fleet.get("/api/v1/robots", headers=KEY)
    assert listing.status_code == 200  # fleet survives; identity is cached knowledge
    # clearing goes through the chaos proxy, which rides the robot's
    # /_emulator surface — that stays reachable by design
    cleared = fleet.delete(f"/_emulator/robots/{robot_id}/faults", headers=KEY)
    assert cleared.status_code == 200
    detail = fleet.get(f"/api/v1/robots/{robot_id}", headers=KEY)
    assert detail.status_code == 200
