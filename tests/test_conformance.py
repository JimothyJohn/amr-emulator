"""Contract conformance: exercise every operation of every tracked spec.

For each (method, path) in the spec, fire a request shaped by the spec itself
(path params from seeded state, bodies synthesized from the body schema) and
assert that the emulator answers with a declared status code and — for JSON
200s — a body that validates against the declared response schema.
"""

from amr_emulator.examples import example_from_schema
from amr_emulator.spec import Operation
from jsonschema import Draft4Validator

from tests.conftest import AUTH_HEADER


def _fill_path(op: Operation, path: str) -> str:
    """Substitute plausible values for path template params."""
    for name, ptype in op.path_param_types().items():
        value = "1" if ptype == "integer" else "emulated-0000-0000-0001-000000000000"
        path = path.replace("{" + name + "}", value)
    return path


def _request_kwargs(spec, op: Operation) -> dict:
    kwargs: dict = {"headers": dict(AUTH_HEADER)}
    if op.body_schema is not None:
        kwargs["json"] = example_from_schema(spec.deref(op.body_schema))
    return kwargs


def test_every_operation_answers_with_a_declared_status(client, spec):
    failures = []
    for op in spec.operations.values():
        url = spec.base_path + _fill_path(op, op.path)
        response = client.request(op.method, url, **_request_kwargs(spec, op))
        declared = set(op.responses) | {200}
        if response.status_code not in declared:
            failures.append(
                f"{op.method} {op.path} -> {response.status_code} not in {sorted(op.responses)}"
            )
    assert not failures, "\n".join(failures[:30])


def _validate_success_body(spec, op, response, failures):
    if response.status_code != op.success_status:
        return
    schema = spec.deref(op.success_schema)
    if not schema:
        return
    body = response.json()
    # MiR specs often declare list endpoints with the element's object
    # schema; real robots return arrays. Validate elements individually.
    instances = body if isinstance(body, list) and schema.get("type") == "object" else [body]
    try:
        for instance in instances:
            Draft4Validator(schema).validate(instance)
    except Exception as exc:
        failures.append(f"{op.method} {op.path}: {str(exc)[:150]}")


def test_get_success_bodies_validate_against_response_schemas(client, spec):
    failures = []
    for op in spec.operations.values():
        if op.method != "GET" or "application/json" not in op.produces[0]:
            continue
        url = spec.base_path + _fill_path(op, op.path)
        response = client.get(url, headers=AUTH_HEADER)
        _validate_success_body(spec, op, response, failures)
    assert not failures, "\n".join(failures[:30])


def test_write_success_bodies_validate_against_response_schemas(client, spec):
    """POST/PUT answers must honor their declared schemas too — the stateful
    overrides (status, mission queue, registers) are the risky ones."""
    failures = []
    for op in spec.operations.values():
        if op.method not in ("POST", "PUT") or "application/json" not in op.produces[0]:
            continue
        url = spec.base_path + _fill_path(op, op.path)
        response = client.request(op.method, url, **_request_kwargs(spec, op))
        _validate_success_body(spec, op, response, failures)
    assert not failures, "\n".join(failures[:30])


def test_mission_queue_lifecycle(client, spec):
    base = spec.base_path
    missions = client.get(f"{base}/missions", headers=AUTH_HEADER).json()
    assert missions, "seeded mission list should not be empty"
    mission_id = missions[0].get("guid", "emulated-0000-0000-0001-000000000000")

    queued = client.post(
        f"{base}/mission_queue", json={"mission_id": mission_id}, headers=AUTH_HEADER
    )
    assert queued.status_code == spec.operations[("POST", "/mission_queue")].success_status
    entry = queued.json()
    assert entry["state"] == "Pending"

    listed = client.get(f"{base}/mission_queue", headers=AUTH_HEADER).json()
    assert any(e.get("id") == entry.get("id") for e in listed)

    status = client.get(f"{base}/status", headers=AUTH_HEADER).json()
    assert status["mission_queue_id"] == entry.get("id")

    cleared = client.delete(f"{base}/mission_queue", headers=AUTH_HEADER)
    assert cleared.status_code in (200, 204)
    assert client.get(f"{base}/mission_queue", headers=AUTH_HEADER).json() == []


def test_registers_read_write(client, spec):
    base = spec.base_path
    registers = client.get(f"{base}/registers", headers=AUTH_HEADER).json()
    assert len(registers) == 200

    updated = client.put(f"{base}/registers/7", json={"value": 42.5}, headers=AUTH_HEADER)
    assert updated.status_code in (200, 201)
    assert updated.json()["value"] == 42.5
    assert client.get(f"{base}/registers/7", headers=AUTH_HEADER).json()["value"] == 42.5

    out_of_range = client.get(f"{base}/registers/500", headers=AUTH_HEADER)
    assert out_of_range.status_code == 404


def test_status_reflects_put(client, spec):
    base = spec.base_path
    original = client.get(f"{base}/status", headers=AUTH_HEADER).json()
    assert original["robot_name"] == "MiR_Emulated"

    # PutStatus declares `name` as the rename field; undeclared fields
    # (like the GET-side robot_name) are ignored, as on a real robot.
    renamed = client.put(f"{base}/status", json={"name": "conformance-bot"}, headers=AUTH_HEADER)
    assert renamed.status_code == 200
    assert client.get(f"{base}/status", headers=AUTH_HEADER).json()["robot_name"] == (
        "conformance-bot"
    )


def test_put_status_choices_are_enforced(client, spec):
    base = spec.base_path
    for body in ({"state_id": 99}, {"mode_id": 1}, {"clear_error": False}):
        response = client.put(f"{base}/status", json=body, headers=AUTH_HEADER)
        assert response.status_code == 400, body
        assert "error_human" in response.json()


def test_unknown_mission_id_cannot_be_enqueued(client, spec):
    base = spec.base_path
    response = client.post(
        f"{base}/mission_queue",
        json={"mission_id": "definitely-not-a-mission"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 400
    assert "Argument error" in response.json()["error_human"]


def test_validation_reports_all_missing_required_fields(client, spec):
    """One 400 names every missing required property, not just the first.

    A client posting an incomplete body (e.g. POST /maps with only a name)
    should learn the full shape of the problem in one round trip instead of
    re-discovering required fields one 400 at a time.
    """
    checked = 0
    for op in spec.operations.values():
        if op.method != "POST" or op.body_schema is None:
            continue
        required = spec.deref(op.body_schema).get("required", [])
        if len(required) < 2:
            continue
        url = spec.base_path + _fill_path(op, op.path)
        response = client.post(url, json={}, headers=dict(AUTH_HEADER))
        assert response.status_code == 400, f"{op.method} {op.path}: {response.status_code}"
        human = response.json()["error_human"]
        omitted = [name for name in required if f"'{name}'" not in human]
        assert not omitted, f"{op.method} {op.path}: error omits {omitted}: {human}"
        checked += 1
    assert checked, "no POST operation with >=2 required body fields exercised"


def _undeclared_keys(spec, op, body) -> set[str]:
    """Response keys the op's success schema does not declare.

    Only meaningful when the schema declares properties and does not opt into
    additionalProperties; list bodies are checked element-by-element (including
    the MiR quirk of list endpoints declared with the element's object schema).
    """
    schema = spec.deref(op.success_schema)
    if schema.get("type") == "array":
        schema = schema.get("items") or {}
    props = schema.get("properties")
    if not isinstance(props, dict) or schema.get("additionalProperties"):
        return set()
    instances = body if isinstance(body, list) else [body]
    extra: set[str] = set()
    for instance in instances:
        if isinstance(instance, dict):
            extra |= set(instance) - set(props)
    return extra


def test_success_bodies_contain_only_declared_fields(client, spec):
    """The emulator must not answer with fields the official spec never
    declares — an integration written against it would then break on a real
    robot. Strict complement of the validate-against-schema tests above
    (Draft-4 validation alone accepts undeclared extras)."""
    failures = []
    for op in spec.operations.values():
        if op.method not in ("GET", "POST", "PUT") or "application/json" not in op.produces[0]:
            continue
        url = spec.base_path + _fill_path(op, op.path)
        response = client.request(op.method, url, **_request_kwargs(spec, op))
        if response.status_code != op.success_status:
            continue
        try:
            body = response.json()
        except ValueError:
            continue
        extra = _undeclared_keys(spec, op, body)
        if extra:
            failures.append(f"{op.method} {op.path}: undeclared fields {sorted(extra)}")
    assert not failures, "\n".join(failures[:30])


def test_mission_queue_replies_are_spec_shaped_and_do_not_echo_undeclared_fields(client, spec):
    """POST /mission_queue and the GET list answer with GetMission_queues —
    and never echo request-body fields the spec does not declare."""
    base = spec.base_path
    mission_id = client.get(f"{base}/missions", headers=AUTH_HEADER).json()[0]["guid"]
    queued = client.post(
        f"{base}/mission_queue",
        json={"mission_id": mission_id, "undeclared_field": "leak"},
        headers=AUTH_HEADER,
    )
    assert queued.status_code == spec.operations[("POST", "/mission_queue")].success_status
    post_op = spec.operations[("POST", "/mission_queue")]
    assert not _undeclared_keys(spec, post_op, queued.json())

    list_op = spec.operations[("GET", "/mission_queue")]
    listed = client.get(f"{base}/mission_queue", headers=AUTH_HEADER).json()
    assert listed
    assert not _undeclared_keys(spec, list_op, listed)

    item_op = next(
        op
        for (method, path), op in spec.operations.items()
        if method == "GET" and path.startswith("/mission_queue/{")
    )
    item = client.get(f"{base}/mission_queue/{queued.json()['id']}", headers=AUTH_HEADER).json()
    assert not _undeclared_keys(spec, item_op, item)

    client.delete(f"{base}/mission_queue", headers=AUTH_HEADER)


def test_route_surface_is_exactly_the_spec_plus_reserved_emulator_paths(client, spec):
    """Everything under the API base path is a spec operation (no invented
    endpoints, none missing); everything else stays on the reserved
    emulator-only paths, outside the official API surface."""
    import re

    from starlette.routing import Route, WebSocketRoute

    served = set()
    for route in client.app.routes:
        if isinstance(route, Route):
            for method in (route.methods or set()) - {"HEAD", "OPTIONS"}:
                served.add((method, re.sub(r"{(\w+):\w+}", r"{\1}", route.path)))
        elif isinstance(route, WebSocketRoute):
            served.add(("WS", route.path))

    expected = {(op.method, spec.base_path + op.path) for op in spec.operations.values()}
    api_served = {r for r in served if r[1].startswith(spec.base_path)}
    assert api_served == expected

    for method, path in served - api_served:
        assert (
            path == "/"
            or path in ("/swagger.json", "/openapi.json")
            or path.startswith("/_emulator/")
        ), f"unexpected non-API route {method} {path}"


def test_generic_crud_round_trip(client, spec):
    base = spec.base_path
    created = client.post(
        f"{base}/missions",
        json={"name": "test mission", "group_id": "emulated-0000-0000-0001-000000000000"},
        headers=AUTH_HEADER,
    )
    assert created.status_code in spec.operations[("POST", "/missions")].responses
    if created.status_code >= 300:
        return
    guid = created.json()["guid"]

    fetched = client.get(f"{base}/missions/{guid}", headers=AUTH_HEADER)
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "test mission"

    deleted = client.delete(f"{base}/missions/{guid}", headers=AUTH_HEADER)
    assert deleted.status_code in (200, 204)
    assert client.get(f"{base}/missions/{guid}", headers=AUTH_HEADER).status_code == 404


def test_no_private_keys_leak_from_any_response(client, spec):
    """Underscore-prefixed keys are emulator-internal storage (e.g. the
    verbatim client body stashed at create time) and must never appear on
    the wire — reads and writes alike."""
    leaked = []
    for op in spec.operations.values():
        if op.method not in ("GET", "POST", "PUT") or "application/json" not in op.produces[0]:
            continue
        url = spec.base_path + _fill_path(op, op.path)
        response = client.request(op.method, url, **_request_kwargs(spec, op))
        try:
            body = response.json()
        except ValueError:
            continue
        for doc in body if isinstance(body, list) else [body]:
            private = sorted(k for k in doc if k.startswith("_")) if isinstance(doc, dict) else []
            if private:
                leaked.append(f"{op.method} {op.path}: {private}")
    assert not leaked, "\n".join(leaked[:20])
