"""Mission simulation + per-session virtual robots.

The simulation is time-derived (no background tasks), so tests freeze
behaviors._now and step it manually — fully deterministic.
"""

import threading

import pytest
from amr_emulator import behaviors
from amr_emulator.app import MAX_SESSIONS, create_app
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
def client():
    return TestClient(create_app("3.8.1"))


def mission_guid(client, headers=AUTH):
    """The robot only queues missions it knows; use the seeded one."""
    r = client.get("/api/v2.0.0/missions", headers=headers)
    assert r.status_code == 200
    return r.json()[0]["guid"]


def enqueue(client, headers=AUTH, **body):
    body.setdefault("mission_id", mission_guid(client, headers))
    r = client.post("/api/v2.0.0/mission_queue", json=body, headers=headers)
    assert r.status_code == 201
    return r.json()


def q_state(client, qid, headers=AUTH):
    r = client.get(f"/api/v2.0.0/mission_queue/{qid}", headers=headers)
    assert r.status_code == 200
    return r.json()["state"]


def status(client, headers=AUTH):
    r = client.get("/api/v2.0.0/status", headers=headers)
    assert r.status_code == 200
    return r.json()


# --- lifecycle ---------------------------------------------------------------


def test_mission_runs_ten_seconds_then_stops(clock, client):
    entry = enqueue(client)
    qid = entry["id"]
    assert entry["state"] == "Pending"

    clock.tick(0.5)  # still inside the pickup lag
    assert q_state(client, qid) == "Pending"

    clock.tick(1.0)  # 1.5s: executing
    assert q_state(client, qid) == "Executing"
    assert status(client)["state_text"] == "Executing"
    assert status(client)["mission_queue_id"] == qid

    clock.tick(9.0)  # 10.5s: 9.5s of execution done, still running
    assert q_state(client, qid) == "Executing"

    clock.tick(1.0)  # 11.5s: past 1s lag + 10s run
    assert q_state(client, qid) == "Done"
    doc = status(client)
    assert doc["state_text"] == "Ready"
    assert doc["state_id"] == 3


def test_missions_run_fifo_one_at_a_time(clock, client):
    first = enqueue(client)["id"]
    second = enqueue(client)["id"]

    clock.tick(2.0)
    assert q_state(client, first) == "Executing"
    assert q_state(client, second) == "Pending"

    clock.tick(10.0)  # 12s: first done (1..11), second executing (11..21)
    assert q_state(client, first) == "Done"
    assert q_state(client, second) == "Executing"

    clock.tick(10.0)  # 22s: all done
    assert q_state(client, second) == "Done"


def test_internal_fields_never_leak(clock, client):
    enqueue(client)
    listing = client.get("/api/v2.0.0/mission_queue", headers=AUTH).json()
    assert listing and all(not k.startswith("_") for e in listing for k in e)


def test_delete_clears_queue_and_status(clock, client):
    enqueue(client)
    clock.tick(2.0)
    deleted = client.delete("/api/v2.0.0/mission_queue", headers=AUTH)
    assert deleted.status_code == 204
    assert client.get("/api/v2.0.0/mission_queue", headers=AUTH).json() == []
    assert status(client)["state_text"] == "Ready"


# --- telemetry coupling ------------------------------------------------------


def test_battery_drains_and_position_moves_while_executing(clock, client):
    before = status(client)
    enqueue(client)
    clock.tick(6.0)  # 5s of execution
    during = status(client)
    assert during["battery_percentage"] < before["battery_percentage"]
    assert during["position"]["x"] == pytest.approx(5.0 + 5 * behaviors.MISSION_SPEED_M_S)
    assert during["velocity"]["linear"] == behaviors.MISSION_SPEED_M_S
    assert during["distance_to_next_target"] > 0

    clock.tick(20.0)  # long done
    after = status(client)
    assert after["velocity"]["linear"] == 0.0
    assert after["moved"] > before["moved"]
    # battery stops draining once the mission is over
    clock.tick(100.0)
    assert status(client)["battery_percentage"] == after["battery_percentage"]


def test_battery_never_drops_below_floor(clock, client):
    # (92.5 - 20) / 0.05%/s = 1450s of execution; 150 missions = 1500s
    for _ in range(150):
        enqueue(client)
    clock.tick(1600.0)
    assert status(client)["battery_percentage"] == behaviors.BATTERY_FLOOR


def test_metrics_reflect_simulation(clock, client):
    enqueue(client)
    clock.tick(6.0)
    text = client.get("/api/v2.0.0/metrics", headers=AUTH).text
    assert "mir_robot_battery_percent 92.25" in text  # 5s * 0.05%/s drained


# --- pause / resume ----------------------------------------------------------


def test_pause_freezes_mission_and_resume_completes_it(clock, client):
    qid = enqueue(client)["id"]
    clock.tick(5.0)  # 4s executed
    pause = client.put("/api/v2.0.0/status", json={"state_id": 4}, headers=AUTH)
    assert pause.status_code == 200
    paused = status(client)
    assert paused["state_text"] == "Pause"
    assert paused["state_id"] == 4

    clock.tick(300.0)  # wall clock races ahead; sim is frozen
    assert q_state(client, qid) == "Executing"
    assert status(client)["state_text"] == "Pause"

    resume = client.put("/api/v2.0.0/status", json={"state_id": 3}, headers=AUTH)
    assert resume.status_code == 200
    clock.tick(5.0)  # 4s + 5s = 9s executed, still going
    assert q_state(client, qid) == "Executing"
    clock.tick(2.0)  # 11s > 10s: done
    assert q_state(client, qid) == "Done"


def test_user_status_writes_survive_simulation(clock, client):
    # Per the spec's PutStatus document, `name` is the field that renames.
    client.put("/api/v2.0.0/status", json={"name": "conveyor-7"}, headers=AUTH)
    enqueue(client)
    clock.tick(3.0)
    doc = status(client)
    assert doc["robot_name"] == "conveyor-7"
    assert doc["state_text"] == "Executing"  # sim owns state, user owns name


def test_undeclared_put_status_fields_are_ignored(clock, client):
    # A real robot only honors PutStatus-declared fields; robot_name is the
    # GET-side name of the `name` field, not a writable one.
    client.put("/api/v2.0.0/status", json={"robot_name": "sneaky"}, headers=AUTH)
    assert status(client)["robot_name"] == "MiR_Emulated"
    client.put("/api/v2.0.0/status", json={"battery_percentage": 1.0}, headers=AUTH)
    assert status(client)["battery_percentage"] == 92.5


# --- sessions: many users, many robots --------------------------------------


def sess(name):
    return {**AUTH, "X-AMR-Session": name}


def test_sessions_are_isolated_robots(clock, client):
    alice_mission = enqueue(client, headers=sess("alice"))["id"]
    clock.tick(3.0)

    # Alice's robot is executing; Bob's and the shared robot are idle.
    assert status(client, sess("alice"))["state_text"] == "Executing"
    assert status(client, sess("bob"))["state_text"] == "Ready"
    assert status(client)["state_text"] == "Ready"
    assert client.get("/api/v2.0.0/mission_queue", headers=sess("bob")).json() == []
    assert client.get("/api/v2.0.0/mission_queue", headers=AUTH).json() == []
    assert q_state(client, alice_mission, headers=sess("alice")) == "Executing"

    # Registers are isolated too.
    client.put("/api/v2.0.0/registers/1", json={"value": 7}, headers=sess("alice"))
    assert client.get("/api/v2.0.0/registers/1", headers=sess("bob")).json()["value"] == 0.0

    # Pausing Alice's robot does not pause Bob's.
    client.put("/api/v2.0.0/status", json={"state_id": 4}, headers=sess("alice"))
    enqueue(client, headers=sess("bob"))
    clock.tick(3.0)
    assert status(client, sess("alice"))["state_text"] == "Pause"
    assert status(client, sess("bob"))["state_text"] == "Executing"


def test_invalid_session_ids_rejected(client):
    # (non-latin-1 ids can't even be sent by httpx; the Lambda adapter path
    # utf-8-encodes headers and the regex rejects them server-side)
    for bad in ["a" * 65, "spaces here", "semi;colon", "a/b", "a\tb"]:
        r = client.get("/api/v2.0.0/status", headers={**AUTH, "X-AMR-Session": bad})
        assert r.status_code == 400, bad


def test_session_count_is_capped(client):
    emulator = client.app.state.emulator
    for i in range(MAX_SESSIONS + 50):
        emulator.state_for(f"s{i}")
    assert len(emulator._sessions) == MAX_SESSIONS
    # oldest evicted, newest retained
    assert "s0" not in emulator._sessions
    assert f"s{MAX_SESSIONS + 49}" in emulator._sessions


def test_concurrent_session_churn_is_safe(client):
    emulator = client.app.state.emulator
    errors = []

    def churn(worker):
        try:
            for i in range(300):
                store = emulator.state_for(f"w{worker}-{i % 40}")
                store.merge_singleton("/registers", {"1": float(worker)})
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=churn, args=(w,)) for w in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(emulator._sessions) <= MAX_SESSIONS


def test_custom_mission_duration(clock):
    quick = TestClient(create_app("3.8.1", mission_duration=2.0))
    qid = enqueue(quick)["id"]
    clock.tick(1.5)
    assert q_state(quick, qid) == "Executing"
    clock.tick(2.0)  # 3.5s > 1s lag + 2s run
    assert q_state(quick, qid) == "Done"


# --- referential integrity: the robot only runs missions it knows -----------


def test_unknown_mission_id_is_rejected(clock, client):
    r = client.post("/api/v2.0.0/mission_queue", json={"mission_id": "no-such-guid"}, headers=AUTH)
    assert r.status_code == 400
    assert "Argument error" in r.json()["error_human"]
    assert client.get("/api/v2.0.0/mission_queue", headers=AUTH).json() == []


def test_created_mission_can_be_enqueued(clock, client):
    created = client.post(
        "/api/v2.0.0/missions",
        json={"name": "patrol west wing", "group_id": "emulated-0000-0000-0001-000000000000"},
        headers=AUTH,
    )
    assert created.status_code == 201
    qid = enqueue(client, mission_id=created.json()["guid"])["id"]
    entry = client.get(f"/api/v2.0.0/mission_queue/{qid}", headers=AUTH).json()
    assert entry["mission_id"] == created.json()["guid"]


def test_per_mission_duration_header_freezes_onto_that_entry(clock, client):
    # A 5s haul via X-AMR-Mission-Duration, then a stock 10s mission: the
    # FIFO timeline honors each entry's own duration.
    short = enqueue(client, headers={**AUTH, "X-AMR-Mission-Duration": "5"})
    stock = enqueue(client)
    clock.tick(5.5)  # 1s lag + 5s: the short entry is in its last moments
    assert q_state(client, short["id"]) == "Executing"
    clock.tick(1.0)
    assert q_state(client, short["id"]) == "Done"
    assert q_state(client, stock["id"]) == "Executing", "stock mission started at 6s"
    clock.tick(9.0)
    assert q_state(client, stock["id"]) == "Executing", "stock entry still runs its full 10s"
    clock.tick(1.0)
    assert q_state(client, stock["id"]) == "Done"


def test_per_mission_duration_scales_battery_and_odometry(clock, client):
    moved_before = status(client)["moved"]
    enqueue(client, headers={**AUTH, "X-AMR-Mission-Duration": "20"})
    clock.tick(21.5)  # lag + 20s executing
    doc = status(client)
    assert doc["battery_percentage"] == pytest.approx(92.5 - 0.05 * 20.0)
    assert doc["moved"] - moved_before == pytest.approx(0.5 * 20.0)


def test_invalid_mission_duration_header_is_400(clock, client):
    mission = mission_guid(client)
    for bad in ("abc", "0", "-5", "3601", "nan", "inf", ""):
        r = client.post(
            "/api/v2.0.0/mission_queue",
            json={"mission_id": mission},
            headers={**AUTH, "X-AMR-Mission-Duration": bad},
        )
        assert r.status_code == 400, bad
        assert "X-AMR-Mission-Duration" in r.json()["error_human"]
    assert client.get("/api/v2.0.0/mission_queue", headers=AUTH).json() == []
    # A valid header on a read is validated but has no effect.
    r = client.get("/api/v2.0.0/status", headers={**AUTH, "X-AMR-Mission-Duration": "5"})
    assert r.status_code == 200


def test_metrics_count_completed_and_aborted_missions(clock, client):
    enqueue(client)
    enqueue(client)
    clock.tick(11.5)  # first Done, second Executing
    metrics = client.get("/api/v2.0.0/metrics", headers=AUTH).text
    assert "mir_robot_missions_completed_total 1" in metrics
    assert "mir_robot_missions_aborted_total 0" in metrics

    client.put("/_emulator/faults", headers=AUTH, json={"faults": ["mission_failure"]})
    client.put("/api/v2.0.0/status", headers=AUTH, json={"clear_error": True})
    metrics = client.get("/api/v2.0.0/metrics", headers=AUTH).text
    assert "mir_robot_missions_completed_total 1" in metrics
    assert "mir_robot_missions_aborted_total 1" in metrics


def test_create_mission_without_group_id_is_rejected_with_the_missing_field(clock, client):
    # Real robots require group_id on PostMissions; the 400 must name it so
    # a client knows what to add rather than guessing at the body schema.
    r = client.post("/api/v2.0.0/missions", json={"name": "no group"}, headers=AUTH)
    assert r.status_code == 400
    assert "group_id" in r.json()["error_human"]
    names = [m["name"] for m in client.get("/api/v2.0.0/missions", headers=AUTH).json()]
    assert "no group" not in names, "a rejected mission must not be created"


# --- queue entry lifecycle metadata ------------------------------------------


def iso(ts: float) -> str:
    import time as _time

    return _time.strftime("%Y-%m-%dT%H:%M:%S", _time.gmtime(ts))


def test_queue_entry_timestamps_follow_the_lifecycle(clock, client):
    qid = enqueue(client)["id"]
    entry = client.get(f"/api/v2.0.0/mission_queue/{qid}", headers=AUTH).json()
    assert entry["ordered"] == iso(T0)
    assert "started" not in entry and "finished" not in entry

    clock.tick(2.0)  # executing since T0+1
    running = client.get(f"/api/v2.0.0/mission_queue/{qid}", headers=AUTH).json()
    assert running["started"] == iso(T0 + 1)
    assert "finished" not in running

    clock.tick(10.0)  # done at T0+11
    done = client.get(f"/api/v2.0.0/mission_queue/{qid}", headers=AUTH).json()
    assert done["state"] == "Done"
    assert done["ordered"] == iso(T0)
    assert done["started"] == iso(T0 + 1)
    assert done["finished"] == iso(T0 + 11)


def test_queue_entry_links_back_to_its_mission(clock, client):
    guid = mission_guid(client)
    qid = enqueue(client, mission_id=guid)["id"]
    entry = client.get(f"/api/v2.0.0/mission_queue/{qid}", headers=AUTH).json()
    if "mission" in entry:  # field exists in every tracked 3.x spec
        assert entry["mission"] == f"/v2.0.0/missions/{guid}"


def test_post_mission_queue_reply_is_the_declared_slim_document(clock, client):
    """The spec's 201 document is GetMission_queues = {id, state, url} —
    no lifecycle extras, and never an echo of undeclared body fields."""
    entry = enqueue(client, undeclared_field="leak")
    assert set(entry) == {"id", "state", "url"}


def test_status_links_to_executing_queue_entry(clock, client):
    qid = enqueue(client)["id"]
    clock.tick(2.0)
    doc = status(client)
    if "mission_queue_url" in doc:
        assert doc["mission_queue_url"] == f"/v2.0.0/mission_queue/{qid}"


def test_deleting_one_entry_recomputes_the_timeline(clock, client):
    first = enqueue(client)["id"]
    second = enqueue(client)["id"]
    clock.tick(2.0)
    assert q_state(client, first) == "Executing"

    gone = client.delete(f"/api/v2.0.0/mission_queue/{first}", headers=AUTH)
    assert gone.status_code == 204
    assert client.get(f"/api/v2.0.0/mission_queue/{first}", headers=AUTH).status_code == 404
    # the executing mission stopped on the spot; the next one takes over
    assert q_state(client, second) == "Executing"

    missing = client.delete("/api/v2.0.0/mission_queue/9999", headers=AUTH)
    assert missing.status_code == 404


def test_delete_on_a_fresh_queue_is_404_not_a_phantom_entry(clock, client):
    r = client.delete("/api/v2.0.0/mission_queue/1", headers=AUTH)
    assert r.status_code == 404
    assert client.get("/api/v2.0.0/mission_queue", headers=AUTH).json() == []


# --- PUT /status: the spec's declared fields and choices ---------------------


def test_manual_control_holds_the_robot(clock, client):
    qid = enqueue(client)["id"]
    clock.tick(3.0)  # 2s executed
    r = client.put("/api/v2.0.0/status", json={"state_id": 11}, headers=AUTH)
    assert r.status_code == 200
    doc = status(client)
    assert doc["state_id"] == 11
    assert doc["state_text"] == "Manualcontrol"

    clock.tick(600.0)  # manual control freezes the sim like pause does
    assert q_state(client, qid) == "Executing"

    client.put("/api/v2.0.0/status", json={"state_id": 3}, headers=AUTH)
    clock.tick(9.0)  # 2s + 9s > 10s: finishes after release
    assert q_state(client, qid) == "Done"


def test_put_status_rejects_undeclared_choices(clock, client):
    for body in ({"state_id": 5}, {"state_id": 99}, {"mode_id": 1}, {"clear_error": False}):
        r = client.put("/api/v2.0.0/status", json=body, headers=AUTH)
        assert r.status_code == 400, body
        assert "Argument error" in r.json()["error_human"]


def test_mode_switch_is_stateful(clock, client):
    r = client.put("/api/v2.0.0/status", json={"mode_id": 3}, headers=AUTH)
    assert r.status_code == 200
    doc = status(client)
    assert doc["mode_id"] == 3
    client.put("/api/v2.0.0/status", json={"mode_id": 7}, headers=AUTH)
    assert status(client)["mode_id"] == 7


def test_clear_error_true_is_accepted(clock, client):
    r = client.put("/api/v2.0.0/status", json={"clear_error": True}, headers=AUTH)
    assert r.status_code == 200
    assert status(client).get("errors", []) == []


def test_put_position_relocalizes_the_robot(clock, client):
    r = client.put(
        "/api/v2.0.0/status",
        json={"position": {"x": 10.0, "y": 3.0, "orientation": 90.0}},
        headers=AUTH,
    )
    assert r.status_code == 200
    pos = status(client)["position"]
    assert (pos["x"], pos["y"], pos["orientation"]) == (10.0, 3.0, 90.0)

    enqueue(client)
    clock.tick(6.0)  # 5s executing at 0.5 m/s = 2.5 m from the new home
    pos = status(client)["position"]
    assert pos["x"] == pytest.approx(10.0 + 2.5)
    assert pos["y"] == 3.0


def test_uptime_advances_with_the_clock(clock, client):
    assert status(client)["uptime"] == 3600
    clock.tick(50.0)
    assert status(client)["uptime"] == 3650
    assert "mir_robot_uptime_seconds_total 3650" in (
        client.get("/api/v2.0.0/metrics", headers=AUTH).text
    )


# --- registers: labels persist alongside values ------------------------------


def test_register_label_and_value_round_trip(clock, client):
    written = client.put(
        "/api/v2.0.0/registers/5", json={"value": 1.5, "label": "conveyor flag"}, headers=AUTH
    )
    assert written.status_code == 200
    doc = client.get("/api/v2.0.0/registers/5", headers=AUTH).json()
    assert doc["value"] == 1.5
    assert doc["label"] == "conveyor flag"

    # POST /registers/{id} (declared in the spec) merges like PUT does.
    client.post("/api/v2.0.0/registers/5", json={"value": 2.0}, headers=AUTH)
    doc = client.get("/api/v2.0.0/registers/5", headers=AUTH).json()
    assert doc["value"] == 2.0
    assert doc["label"] == "conveyor flag"


def test_register_bad_types_are_400(clock, client):
    assert (
        client.put("/api/v2.0.0/registers/5", json={"value": True}, headers=AUTH).status_code == 400
    )


# --- parallel developers, one emulator ---------------------------------------


def test_parallel_sessions_run_full_lifecycles_without_crosstalk(clock):
    app = create_app("3.8.1")
    queue_ids: dict[str, int] = {}
    errors: list[Exception] = []

    def worker(name: str) -> None:
        try:
            c = TestClient(app)
            entry = c.post(
                "/api/v2.0.0/mission_queue",
                json={"mission_id": mission_guid(c, sess(name))},
                headers=sess(name),
            )
            assert entry.status_code == 201, entry.text
            queue_ids[name] = entry.json()["id"]
        except Exception as exc:  # surfaced after join
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(f"user-{i}",)) for i in range(12)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors

    clock.tick(3.0)
    verify = TestClient(app)
    for name, qid in queue_ids.items():
        listing = verify.get("/api/v2.0.0/mission_queue", headers=sess(name)).json()
        assert [e["id"] for e in listing] == [qid], f"{name} sees exactly its own queue"
        assert status(verify, sess(name))["state_text"] == "Executing"
    assert verify.get("/api/v2.0.0/mission_queue", headers=AUTH).json() == []
    assert status(verify)["state_text"] == "Ready"
