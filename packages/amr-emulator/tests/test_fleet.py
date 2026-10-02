"""MiR Fleet Enterprise emulator: auth, dispatch, isolation, cross-emulator truth.

The fleet controls its embedded robots over their real REST API, so these
tests repeatedly verify BOTH sides of an interaction: what the fleet reports
and what the robot itself serves. The mission simulation is time-derived;
tests freeze behaviors._now and step it manually — fully deterministic.
"""

import threading

import pytest
from amr_emulator import behaviors
from amr_emulator.auth import expected_token
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
from starlette.testclient import TestClient

KEY = {"x-api-key": DEFAULT_API_KEY}
ROBOT_AUTH = {"Authorization": f"Basic {expected_token('distributor', 'distributor')}"}
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
def app():
    return create_fleet_app("1.5.0")


@pytest.fixture()
def fleet(app):
    return TestClient(app)


def robot_client(app, index: int = 0) -> TestClient:
    """A client talking DIRECTLY to one of the fleet's embedded robots."""
    return TestClient(app.state.emulator.robots[index].app)


def site_mission_id(fleet) -> str:
    return fleet.get("/api/v1/site/mission", headers=KEY).json()["missions"][0]["id"]


def post_order(fleet, mission_id, headers=None, **order):
    body = {"serial-order": {"phases": [{"mission-id": mission_id}], **order}}
    return fleet.post("/api/v1/serial-order", headers=headers or KEY, json=body)


# ---- auth --------------------------------------------------------------------


def test_no_api_key_is_401(fleet):
    assert fleet.get("/api/v1/robots").status_code == 401


def test_wrong_and_empty_api_keys_are_401(fleet):
    assert fleet.get("/api/v1/robots", headers={"x-api-key": "nope"}).status_code == 401
    assert fleet.get("/api/v1/robots", headers={"x-api-key": ""}).status_code == 401


def test_robot_basic_auth_does_not_open_the_fleet(fleet):
    # The robot credential scheme must not be accepted by the fleet API.
    assert fleet.get("/api/v1/robots", headers=ROBOT_AUTH).status_code == 401


def test_index_and_specs_are_public_but_api_is_not(fleet):
    assert fleet.get("/").status_code == 200
    assert fleet.get("/openapi.json").json()["info"]["title"].startswith("MiR Fleet")
    assert fleet.get("/api/v1/order").status_code == 401


# ---- robots: fleet view vs robot truth ----------------------------------------


def test_robots_lists_embedded_robots_with_identity(fleet):
    robots = fleet.get("/api/v1/robots", headers=KEY).json()["robots"]
    assert len(robots) == 2
    for required in ("robot-id", "serial-number", "name", "model", "software-version", "ip"):
        assert all(r.get(required) for r in robots)
    assert robots[0]["robot-id"] != robots[1]["robot-id"]
    assert robots[0]["name"] == "MiR_Emulated_1"


def test_robot_rename_on_robot_api_shows_up_in_fleet(app, fleet):
    robot = robot_client(app, 0)
    put = robot.put("/api/v2.0.0/status", headers=ROBOT_AUTH, json={"name": "warehouse-7"})
    assert put.status_code == 200
    names = {r["name"] for r in fleet.get("/api/v1/robots", headers=KEY).json()["robots"]}
    assert "warehouse-7" in names


def test_robot_detail_carries_live_runtime_data(fleet):
    robots = fleet.get("/api/v1/robots", headers=KEY).json()["robots"]
    detail = fleet.get(f"/api/v1/robots/{robots[0]['robot-id']}", headers=KEY).json()
    assert detail["robot-identity"]["robot-id"] == robots[0]["robot-id"]
    assert detail["runtime-data"]["battery-percentage"] == pytest.approx(92.5)
    assert detail["robot-end-state"] == "Idle"


def test_unknown_robot_is_404(fleet):
    assert fleet.get("/api/v1/robots/definitely-not-a-robot", headers=KEY).status_code == 404


# ---- serial orders drive real robot mission queues -----------------------------


def test_serial_order_lands_in_the_robot_mission_queue(clock, app, fleet):
    mission = site_mission_id(fleet)
    created = post_order(fleet, mission)
    assert created.status_code == 201
    assert created.json()["id"]

    # Robot truth: exactly one of the two robots now holds the mission. The
    # list document is the spec's slim {id, state, url}; the full entry (with
    # mission_id) lives at the item endpoint.
    holders = [
        (i, entry)
        for i in range(2)
        for entry in robot_client(app, i)
        .get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
        .json()
    ]
    assert len(holders) == 1
    robot_index, entry = holders[0]
    item = (
        robot_client(app, robot_index)
        .get(f"/api/v2.0.0/mission_queue/{entry['id']}", headers=ROBOT_AUTH)
        .json()
    )
    assert item["mission_id"] == mission


def test_order_lifecycle_follows_the_robot_simulation(clock, fleet):
    mission = site_mission_id(fleet)
    post_order(fleet, mission)

    def status():
        orders = fleet.get("/api/v1/order", headers=KEY).json()
        assert len(orders) == 1
        return orders[0]

    assert status()["order-status"] == "Pending"  # inside the pickup lag
    clock.tick(2.0)
    executing = status()
    assert executing["order-status"] == "Executing"
    assert executing["order-started"]
    clock.tick(10.0)
    finished = status()
    assert finished["order-status"] == "Finished"
    assert finished["order-finished"]
    assert finished["mission-id"] == mission


def test_explicit_robot_id_targets_that_robot(clock, app, fleet):
    mission = site_mission_id(fleet)
    second = fleet.get("/api/v1/robots", headers=KEY).json()["robots"][1]["robot-id"]
    assert post_order(fleet, mission, **{"robot-id": second}).status_code == 201
    first_queue = robot_client(app, 0).get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
    second_queue = robot_client(app, 1).get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
    assert first_queue.json() == []
    assert len(second_queue.json()) == 1


def test_unknown_mission_is_rejected_like_the_robot_rejects_it(fleet):
    response = post_order(fleet, "emulated-ffff-ffff-ffff-000000000000")
    assert response.status_code == 400


def test_unknown_robot_id_is_400(fleet):
    mission = site_mission_id(fleet)
    response = post_order(fleet, mission, **{"robot-id": "not-a-robot"})
    assert response.status_code == 400


def test_duplicate_serial_order_id_is_409(clock, fleet):
    mission = site_mission_id(fleet)
    assert post_order(fleet, mission, id="order-A").status_code == 201
    assert post_order(fleet, mission, id="order-A").status_code == 409


def test_body_with_unknown_top_level_key_is_400(fleet):
    # additionalProperties: false in the official schema must be enforced.
    response = fleet.post(
        "/api/v1/serial-order",
        headers=KEY,
        json={"serial-order": {"phases": []}, "surprise": True},
    )
    assert response.status_code == 400


def test_nullable_fields_accept_explicit_null(clock, fleet):
    # OpenAPI 3 nullable must not be rejected by draft-4 validation.
    mission = site_mission_id(fleet)
    response = post_order(fleet, mission, **{"robot-id": None})
    assert response.status_code == 201


def test_get_serial_order_echoes_phases(clock, fleet):
    mission = site_mission_id(fleet)
    serial_id = post_order(fleet, mission, id="so-echo").json()["id"]
    doc = fleet.get(f"/api/v1/serial-order/{serial_id}", headers=KEY).json()
    assert doc["id"] == "so-echo"
    assert doc["phases"][0]["mission-id"] == mission


def test_abort_removes_the_mission_from_the_robot(clock, app, fleet):
    mission = site_mission_id(fleet)
    serial_id = post_order(fleet, mission).json()["id"]
    deleted = fleet.delete(f"/api/v1/serial-order/{serial_id}", headers=KEY)
    assert deleted.status_code in (200, 202, 204)
    order = fleet.get("/api/v1/order", headers=KEY).json()[0]
    assert order["order-status"] == "Aborted"
    for i in range(2):
        queue = robot_client(app, i).get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
        assert queue.json() == []


def test_finished_orders_survive_abort(clock, fleet):
    mission = site_mission_id(fleet)
    serial_id = post_order(fleet, mission).json()["id"]
    clock.tick(30.0)  # long past pickup lag + execution
    fleet.delete(f"/api/v1/serial-order/{serial_id}", headers=KEY)
    assert fleet.get("/api/v1/order", headers=KEY).json()[0]["order-status"] == "Finished"


# ---- sessions compose across fleet and robots ----------------------------------


def test_sessions_isolate_fleet_and_robots(clock, app, fleet):
    mission = site_mission_id(fleet)
    a, b = {**KEY, "X-AMR-Session": "crew-a"}, {**KEY, "X-AMR-Session": "crew-b"}
    assert post_order(fleet, mission, headers=a).status_code == 201

    assert len(fleet.get("/api/v1/order", headers=a).json()) == 1
    assert fleet.get("/api/v1/order", headers=b).json() == []
    assert fleet.get("/api/v1/order", headers=KEY).json() == []

    # Robot truth: the mission lives only in session crew-a's virtual robot.
    robot = robot_client(app, 0)
    in_a = robot.get("/api/v2.0.0/mission_queue", headers={**ROBOT_AUTH, "X-AMR-Session": "crew-a"})
    default = robot.get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
    assert len(in_a.json()) == 1
    assert default.json() == []


def test_invalid_session_id_is_400(fleet):
    bad = {**KEY, "X-AMR-Session": "no spaces allowed!"}
    assert fleet.get("/api/v1/order", headers=bad).status_code == 400


def test_concurrent_orders_lose_nothing(clock, fleet):
    mission = site_mission_id(fleet)
    results: list[int] = []

    def fire(n: int) -> None:
        response = post_order(fleet, mission, id=f"burst-{n}")
        results.append(response.status_code)

    threads = [threading.Thread(target=fire, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results == [201] * 8
    assert len(fleet.get("/api/v1/order", headers=KEY).json()) == 8


# ---- the rest of the surface stays spec-faithful --------------------------------


def test_generic_crud_enforces_the_official_schema(fleet):
    # Valid group-request → accepted by the generic spec-driven engine.
    ok = fleet.post("/api/v1/group", headers=KEY, json={"group": {"name": "night-shift"}})
    assert ok.status_code in (200, 201, 202)
    # Schema violations must be rejected, not absorbed: name is required...
    assert fleet.post("/api/v1/group", headers=KEY, json={"group": {}}).status_code == 400
    # ...and additionalProperties is false.
    bad = fleet.post("/api/v1/group", headers=KEY, json={"group": {"name": "x"}, "extra": 1})
    assert bad.status_code == 400
    listing = fleet.get("/api/v1/site/position", headers=KEY)
    assert listing.status_code == 200


def test_system_version_reports_fleet_version(fleet):
    doc = fleet.get("/api/v1/system/version", headers=KEY).json()
    assert doc["version"] == "1.5.0"


def test_every_fleet_version_boots_and_routes_its_own_operations():
    # Version faithfulness: each fleet serves exactly its spec's surface —
    # e.g. /api/v1/robots only exists from 1.4.0 on.
    from amr_emulator import registry

    for version in registry.fleet_supported_versions():
        app = create_fleet_app(version)
        client = TestClient(app)
        doc = client.get("/openapi.json").json()
        assert doc["openapi"].startswith("3")
        index = client.get("/").json()
        assert index["kind"] == "fleet"
        assert index["emulated_fleet_version"] == version
        assert index["official_docs"].startswith("https://supportportal")
        spec = app.state.emulator.spec
        gettable = [
            op.path for op in spec.operations.values() if op.method == "GET" and "{" not in op.path
        ]
        assert gettable, version
        for path in gettable:
            status = client.get(path, headers=KEY).status_code
            assert status != 404, f"{version} {path} is not routed"


def test_robot_versions_are_configurable(fleet_versions=("3.8.1", "2.14.7")):
    app = create_fleet_app("1.5.0", robot_versions=fleet_versions)
    client = TestClient(app)
    robots = client.get("/api/v1/robots", headers=KEY).json()["robots"]
    assert [r["software-version"] for r in robots] == list(fleet_versions)


def test_custom_api_key_replaces_the_default():
    client = TestClient(create_fleet_app("1.5.0", api_key="s3cret"))
    assert client.get("/api/v1/robots", headers=KEY).status_code == 401
    assert client.get("/api/v1/robots", headers={"x-api-key": "s3cret"}).status_code == 200


# ---- edge cases: atomicity, cross-generation fleets, adversarial inputs --------


def test_failed_multiphase_dispatch_enqueues_nothing(clock, app, fleet):
    # Atomicity: if any phase is invalid, NO mission may reach a robot.
    mission = site_mission_id(fleet)
    response = fleet.post(
        "/api/v1/serial-order",
        headers=KEY,
        json={
            "serial-order": {
                "phases": [
                    {"mission-id": mission},
                    {"mission-id": "emulated-ffff-ffff-ffff-000000000000"},
                ]
            }
        },
    )
    assert response.status_code == 400
    for i in range(2):
        queue = robot_client(app, i).get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
        assert queue.json() == [], "a failed order must not leave partial dispatch behind"
    assert fleet.get("/api/v1/order", headers=KEY).json() == []


def test_multiphase_order_runs_fifo_on_one_robot(clock, app, fleet):
    mission = site_mission_id(fleet)
    robot_id = fleet.get("/api/v1/robots", headers=KEY).json()["robots"][0]["robot-id"]
    response = fleet.post(
        "/api/v1/serial-order",
        headers=KEY,
        json={
            "serial-order": {
                "robot-id": robot_id,
                "phases": [{"mission-id": mission}, {"mission-id": mission}],
            }
        },
    )
    assert response.status_code == 201
    clock.tick(2.0)  # first executing, second pending (FIFO, one robot)
    statuses = sorted(o["order-status"] for o in fleet.get("/api/v1/order", headers=KEY).json())
    assert statuses == ["Executing", "Pending"]
    clock.tick(10.0)  # first finished, second executing
    statuses = sorted(o["order-status"] for o in fleet.get("/api/v1/order", headers=KEY).json())
    assert statuses == ["Executing", "Finished"]


def test_round_robin_spreads_orders_across_robots(clock, app, fleet):
    mission = site_mission_id(fleet)
    assert post_order(fleet, mission).status_code == 201
    assert post_order(fleet, mission).status_code == 201
    for i in range(2):
        queue = robot_client(app, i).get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
        assert len(queue.json()) == 1, f"robot {i} should hold exactly one mission"


def test_cross_generation_fleet_dispatches_to_2x_robots(clock):
    # A fleet managing one 3.x and one 2.x robot — both must accept orders.
    app = create_fleet_app("1.5.0", robot_versions=("3.8.1", "2.10.5.8"))
    fleet = TestClient(app)
    robots = fleet.get("/api/v1/robots", headers=KEY).json()["robots"]
    assert [r["software-version"] for r in robots] == ["3.8.1", "2.10.5.8"]
    mission = site_mission_id(fleet)
    for robot in robots:
        response = post_order(fleet, mission, **{"robot-id": robot["robot-id"]})
        assert response.status_code == 201, robot["software-version"]
    for i in range(2):
        queue = robot_client(app, i).get("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
        assert len(queue.json()) == 1


def test_robot_side_queue_clear_degrades_order_to_waiting(clock, app, fleet):
    # An operator wiping the robot's queue directly must not crash the fleet
    # view — the order degrades to Waiting (no robot truth to derive from).
    mission = site_mission_id(fleet)
    post_order(fleet, mission)
    robot_client(app, 0).delete("/api/v2.0.0/mission_queue", headers=ROBOT_AUTH)
    orders = fleet.get("/api/v1/order", headers=KEY).json()
    assert orders[0]["order-status"] == "Waiting"


def test_mission_created_on_robot_appears_in_site_missions(clock, app, fleet):
    robot = robot_client(app, 0)
    created = robot.post(
        "/api/v2.0.0/missions",
        headers=ROBOT_AUTH,
        json={"name": "hot-swap-mission", "group_id": "emulated"},
    )
    assert created.status_code in (200, 201)
    names = {m["name"] for m in fleet.get("/api/v1/site/mission", headers=KEY).json()["missions"]}
    assert "hot-swap-mission" in names


def test_unknown_order_and_serial_order_are_404(fleet):
    order = fleet.get("/api/v1/order/nope", headers=KEY)
    serial = fleet.get("/api/v1/serial-order/nope", headers=KEY)
    deleted = fleet.delete("/api/v1/serial-order/nope", headers=KEY)
    assert (order.status_code, serial.status_code, deleted.status_code) == (404, 404, 404)


def test_hostile_api_keys_fail_closed(fleet):
    # Only transmissible header values reach the server; non-ASCII and control
    # bytes are already refused at the HTTP layer. What does arrive must be
    # compared exactly (no strip, no prefix match, no case folding).
    hostiles = ("distributor" * 500, "distributor ", " distributor", "Distributor", "distributo")
    for hostile in hostiles:
        response = fleet.get("/api/v1/robots", headers={"x-api-key": hostile})
        assert response.status_code == 401, repr(hostile)


def test_oversized_body_is_rejected(fleet):
    huge = '{"serial-order": {"phases": [{"mission-id": "' + "a" * (2 * 1024 * 1024) + '"}]}}'
    response = fleet.post(
        "/api/v1/serial-order",
        headers={**KEY, "Content-Type": "application/json"},
        content=huge,
    )
    assert response.status_code == 400


def test_sessions_do_not_leak_under_concurrency(clock, fleet):
    mission = site_mission_id(fleet)
    errors: list[str] = []

    def crew(name: str) -> None:
        headers = {**KEY, "X-AMR-Session": name}
        for n in range(3):
            r = post_order(fleet, mission, headers=headers, id=f"{name}-{n}")
            if r.status_code != 201:
                errors.append(f"{name}-{n}: {r.status_code}")
        seen = fleet.get("/api/v1/order", headers=headers).json()
        if len(seen) != 3 or any(not o["order-id"] for o in seen):
            errors.append(f"{name}: saw {len(seen)} orders")

    threads = [threading.Thread(target=crew, args=(f"crew-{i}",)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert fleet.get("/api/v1/order", headers=KEY).json() == []  # default robot untouched


# ---- the Top Module and Compatibility APIs share the one fleet ------------------


def test_extra_apis_require_the_same_api_key(fleet):
    assert fleet.get("/api/v1/top-module/status").status_code == 401
    assert fleet.get("/compatibility_api/v1/missions").status_code == 401
    assert fleet.get("/api/v1/top-module/status", headers=KEY).status_code == 200
    assert fleet.get("/compatibility_api/v1/missions", headers=KEY).status_code == 200


def test_extra_api_documents_served_verbatim(fleet):
    top = fleet.get("/openapi_topmodule_v1.json").json()
    compat = fleet.get("/openapi_compatibility_v1.json").json()
    assert top["info"]["title"] == "Top Module API v1"
    assert compat["info"]["title"] == "MiR Fleet Compatibility API"
    index = fleet.get("/").json()
    assert [a["name"] for a in index["apis"]] == ["integration", "top_module", "compatibility"]


def test_extra_apis_share_fleet_sessions(fleet):
    session = {**KEY, "X-AMR-Session": "crew-a"}
    created = fleet.post(
        "/api/v1/top-module/event",
        headers=session,
        json={},
    )
    assert created.status_code < 500
    # the recorder (fleet-level state) sees steps from every API family
    fleet.put("/_emulator/recorder", headers=session, json={"recording": True})
    fleet.get("/api/v1/system/version", headers=session)
    fleet.get("/api/v1/top-module/status", headers=session)
    fleet.get("/compatibility_api/v1/missions", headers=session)
    steps = fleet.get("/_emulator/recorder", headers=session).json()["steps"]
    assert [s["path"] for s in steps] == [
        "/api/v1/system/version",
        "/api/v1/top-module/status",
        "/compatibility_api/v1/missions",
    ]


def test_every_fleet_version_routes_its_extra_apis():
    from amr_emulator import registry

    for version in registry.fleet_supported_versions():
        app = create_fleet_app(version)
        client = TestClient(app)
        for op in app.state.all_operations:
            if op.method == "GET" and "{" not in op.path:
                assert client.get(op.path, headers=KEY).status_code != 404, f"{version} {op.path}"


def test_fleet_route_surface_is_exactly_the_specs_plus_reserved_paths():
    """Every served API route is an operation of the integration, top-module,
    or compatibility spec; emulator extras stay on reserved paths outside the
    official API surface."""
    import re

    from amr_emulator import registry
    from amr_emulator.spec import load_spec
    from starlette.routing import Route

    for version in registry.fleet_supported_versions():
        app = create_fleet_app(version)
        served = set()
        for route in app.routes:
            if isinstance(route, Route):
                for method in (route.methods or set()) - {"HEAD", "OPTIONS"}:
                    served.add((method, re.sub(r"{(\w+):\w+}", r"{\1}", route.path)))

        expected = set()
        doc_paths = {"/", "/openapi.json", "/openapi_v1.json", "/swagger.json"}
        v, path = registry.fleet_spec_path(version)
        specs = [load_spec(path, v)]
        for record in registry.fleet_extra_specs(v):
            specs.append(load_spec(record["path"], v))
            doc_paths.add("/" + record["file"].rsplit("/", 1)[-1])
        for spec in specs:
            expected |= {(op.method, spec.base_path + op.path) for op in spec.operations.values()}

        api_served = {
            r for r in served if not r[1].startswith("/_emulator/") and r[1] not in doc_paths
        }
        assert api_served == expected, f"fleet {version}"
        for _method, extra_path in served - api_served:
            assert extra_path in doc_paths or extra_path.startswith("/_emulator/"), (
                f"fleet {version}: unexpected non-API route {extra_path}"
            )
