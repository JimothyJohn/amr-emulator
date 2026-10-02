"""Path realism: a mission whose move actions reference named positions
reports coordinates that traverse the waypoint polyline — not a straight
line, and not the canned patrol loop.

Wiring is the official one end to end: POST /positions defines the site's
named positions, POST /missions/{id}/actions attaches move actions
(parameters [{"id": "position", "value": <guid>}], ordered by priority),
and GET /status interpolates along home -> waypoint1 -> ... -> waypointN
while the mission executes, resting at the final waypoint after Done.
"""

import pytest
from amr_emulator import behaviors
from amr_emulator.app import create_app
from amr_emulator.auth import expected_token
from starlette.testclient import TestClient

AUTH = {"Authorization": f"Basic {expected_token('distributor', 'distributor')}"}
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
def client(clock):
    return TestClient(create_app("3.8.1"))


def make_position(client, name, x, y, orientation=0.0):
    return client.post(
        "/api/v2.0.0/positions",
        json={
            "name": name,
            "map_id": "emulated-map",
            "pos_x": x,
            "pos_y": y,
            "orientation": orientation,
            "type_id": 0,
        },
        headers=AUTH,
    ).json()["guid"]


def make_waypoint_mission(client, *position_guids):
    mission = client.post(
        "/api/v2.0.0/missions",
        json={"name": "waypoint run", "group_id": "test"},
        headers=AUTH,
    ).json()["guid"]
    for i, guid in enumerate(position_guids, start=1):
        response = client.post(
            f"/api/v2.0.0/missions/{mission}/actions",
            json={
                "action_type": "move",
                "mission_id": mission,
                "priority": i,
                "parameters": [{"id": "position", "value": guid}],
            },
            headers=AUTH,
        )
        assert response.status_code in (200, 201)
    return mission


def enqueue(client, mission, duration=100):
    return client.post(
        "/api/v2.0.0/mission_queue",
        json={"mission_id": mission},
        headers={**AUTH, "X-AMR-Mission-Duration": str(duration)},
    ).json()["id"]


def position_of(client):
    p = client.get("/api/v2.0.0/status", headers=AUTH).json()["position"]
    return p["x"], p["y"], p["orientation"]


def test_executing_mission_traverses_the_waypoint_polyline_not_a_straight_line(client, clock):
    # home (5,5) -> A (10,5) -> B (10,15): an L, total length 15
    a = make_position(client, "A", 10.0, 5.0)
    b = make_position(client, "B", 10.0, 15.0)
    mission = make_waypoint_mission(client, a, b)
    enqueue(client, mission, duration=100)

    clock.tick(1 + 25)  # 1 s pending lag + 25% of the run
    x, y, heading = position_of(client)
    assert (x, y) == (pytest.approx(8.75), pytest.approx(5.0))  # first leg, heading east
    assert heading == pytest.approx(0.0)

    clock.tick(25)  # 50% of the run: 7.5 of 15 m -> on the second leg
    x, y, heading = position_of(client)
    assert (x, y) == (pytest.approx(10.0), pytest.approx(7.5))
    assert heading == pytest.approx(90.0)
    # a straight line home->B would put the midpoint at (7.5, 10): the path
    # is the site's polyline, not a chord
    assert (x, y) != (pytest.approx(7.5), pytest.approx(10.0))


def test_robot_rests_at_the_final_waypoint_after_done(client, clock):
    a = make_position(client, "A", 10.0, 5.0)
    b = make_position(client, "B", 10.0, 15.0)
    mission = make_waypoint_mission(client, a, b)
    enqueue(client, mission, duration=100)
    clock.tick(200)
    x, y, _ = position_of(client)
    assert (x, y) == (pytest.approx(10.0), pytest.approx(15.0))
    status = client.get("/api/v2.0.0/status", headers=AUTH).json()
    assert status["state_text"] == "Ready"


def test_consecutive_waypoint_missions_chain_their_anchors(client, clock):
    a = make_position(client, "A", 10.0, 5.0)
    c = make_position(client, "C", 10.0, 25.0)
    first = make_waypoint_mission(client, a)
    second = make_waypoint_mission(client, c)
    enqueue(client, first, duration=100)
    clock.tick(150)  # first Done, robot at A
    enqueue(client, second, duration=100)
    clock.tick(51)  # halfway through the second: A (10,5) -> C (10,25)
    x, y, _ = position_of(client)
    assert (x, y) == (pytest.approx(10.0), pytest.approx(15.0))


def test_missions_without_move_actions_keep_the_patrol_model(client, clock):
    mission = client.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    client.post(
        "/api/v2.0.0/mission_queue",
        json={"mission_id": mission},
        headers={**AUTH, "X-AMR-Mission-Duration": "100"},
    )
    clock.tick(26)
    x, y, _ = position_of(client)
    assert y == pytest.approx(5.0)  # patrol stays on the out-and-back segment
    assert x != pytest.approx(5.0)  # but the robot moved


def test_paused_robot_freezes_on_the_polyline(client, clock):
    a = make_position(client, "A", 10.0, 5.0)
    mission = make_waypoint_mission(client, a)
    enqueue(client, mission, duration=100)
    clock.tick(1 + 50)
    x1, y1, _ = position_of(client)
    client.put("/api/v2.0.0/status", json={"state_id": 4}, headers=AUTH)
    clock.tick(30)
    x2, y2, _ = position_of(client)
    assert (x1, y1) == (x2, y2)


def test_put_action_retargets_the_waypoint_and_leaks_no_private_keys(client, clock):
    a = make_position(client, "A", 10.0, 5.0)
    c = make_position(client, "C", 10.0, 25.0)
    mission = make_waypoint_mission(client, a)
    action = client.get(f"/api/v2.0.0/missions/{mission}/actions", headers=AUTH).json()[0]["guid"]
    updated = client.put(
        f"/api/v2.0.0/missions/{mission}/actions/{action}",
        json={"parameters": [{"id": "position", "value": c}]},
        headers=AUTH,
    )
    assert updated.status_code == 200
    assert not any(k.startswith("_") for k in updated.json())
    enqueue(client, mission, duration=100)
    clock.tick(1 + 50)  # halfway: home (5,5) -> C (10,25)
    x, y, _ = position_of(client)
    assert (x, y) != (pytest.approx(7.5), pytest.approx(5.0))  # not headed to A
    # halfway along home->C (length ~20.6): past the midpoint of the segment
    assert y == pytest.approx(15.0, abs=0.5)
