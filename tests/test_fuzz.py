"""Adversarial fuzz: whatever a client throws at it, the emulator never 5xxs.

Deterministic (derandomize=True) so CI is reproducible; the property must hold
regardless of accumulated state, so all examples share one app per version.
"""

import json
import string
from urllib.parse import quote

import pytest
from amr_emulator.app import create_app
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from starlette.testclient import TestClient

from tests.conftest import ALL_VERSIONS, AUTH_HEADER

FUZZ_SETTINGS = settings(
    max_examples=120,
    derandomize=True,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)

_weird_text = st.text(
    alphabet=st.one_of(
        st.sampled_from(string.printable),
        st.characters(min_codepoint=0x80, max_codepoint=0x2FF),
        st.sampled_from(["😀", "🤖", "\U0001f680", "\x00", "\x1b"]),
    ),
    max_size=40,
)

_ATTACK_STRINGS = [
    "../",
    "../../../../etc/passwd",
    "%2e%2e%2f",
    "..%2f..%2f",
    "\x00",
    "\r\nSet-Cookie: pwned=1",
    "' OR '1'='1",
    '";drop table missions;--',
]

_param_value = st.one_of(
    _weird_text,
    st.sampled_from(_ATTACK_STRINGS),
    st.integers(-(2**63), 2**63).map(str),
    st.sampled_from(["1", "0", "-1", "999999999999", "emulated-0000-0000-0001-000000000000", ""]),
)

_json_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(-(2**53), 2**53),
    st.floats(allow_nan=False, allow_infinity=False),
    _weird_text,
)
_json_body = st.recursive(
    _json_scalars,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(_weird_text, children, max_size=4),
    ),
    max_leaves=10,
)

_payload = st.one_of(
    st.none(),
    st.just(b""),
    st.binary(max_size=200),
    _json_body.map(lambda v: json.dumps(v).encode()),
)


@pytest.fixture(params=ALL_VERSIONS, scope="module")
def fuzz_client(request):
    app = create_app(request.param)
    ops = list(app.state.emulator.spec.operations.values())
    base = app.state.emulator.spec.base_path
    with TestClient(app, base_url="http://emulator.test", raise_server_exceptions=False) as client:
        yield client, ops, base


def _url(base: str, op, values: list[str]) -> str:
    path = op.path
    names = list(op.path_param_types())
    for i, name in enumerate(names):
        path = path.replace("{" + name + "}", quote(values[i % len(values)] or "x", safe=""))
    return base + path


@FUZZ_SETTINGS
@given(
    op_index=st.integers(min_value=0),
    values=st.lists(_param_value, min_size=1, max_size=3),
    payload=_payload,
    authed=st.booleans(),
)
def test_never_5xx_and_errors_stay_json(fuzz_client, op_index, values, payload, authed):
    client, ops, base = fuzz_client
    op = ops[op_index % len(ops)]
    headers = dict(AUTH_HEADER) if authed else {}
    headers["Content-Type"] = "application/json"

    response = client.request(op.method, _url(base, op, values), content=payload, headers=headers)

    assert response.status_code < 500, f"{op.method} {op.path} -> {response.status_code}"
    if response.status_code >= 400:
        body = response.json()  # error responses must stay machine-readable
        assert "error_code" in body


# httpx only sends ASCII header values; non-ASCII fails client-side before the
# server sees it. High-byte fuzz of the verifier itself lives in
# packages/amr-emulator/tests/test_auth.py.
_header_text = st.text(alphabet=st.characters(min_codepoint=0x20, max_codepoint=0x7E), max_size=100)


@FUZZ_SETTINGS
@given(header=st.one_of(_header_text, st.binary(max_size=100).map(lambda b: b.hex())))
def test_garbage_auth_never_authenticates_or_crashes(fuzz_client, header):
    client, _ops, base = fuzz_client
    response = client.get(f"{base}/status", headers={"Authorization": header})
    assert response.status_code == 401
    assert response.json()["error_code"] == "401"


@FUZZ_SETTINGS
@given(path=_weird_text)
def test_unknown_paths_never_5xx(fuzz_client, path):
    client, _ops, base = fuzz_client
    response = client.get(base + "/" + quote(path, safe="/"), headers=AUTH_HEADER)
    assert response.status_code < 500


# ---- the fleet surface holds the same invariant --------------------------------

from amr_emulator import registry  # noqa: E402
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app  # noqa: E402


@pytest.fixture(params=registry.fleet_supported_versions(), scope="module")
def fleet_fuzz_client(request):
    app = create_fleet_app(request.param)
    ops = list(app.state.all_operations)  # integration + top module + compatibility
    base = app.state.emulator.spec.base_path  # "" — fleet paths are absolute
    with TestClient(app, base_url="http://fleet.test", raise_server_exceptions=False) as client:
        yield client, ops, base


@FUZZ_SETTINGS
@given(
    op_index=st.integers(min_value=0),
    values=st.lists(_param_value, min_size=1, max_size=3),
    payload=_payload,
    authed=st.booleans(),
)
def test_fleet_never_5xx_and_errors_stay_json(fleet_fuzz_client, op_index, values, payload, authed):
    client, ops, base = fleet_fuzz_client
    op = ops[op_index % len(ops)]
    headers = {"x-api-key": DEFAULT_API_KEY} if authed else {}
    headers["Content-Type"] = "application/json"

    response = client.request(op.method, _url(base, op, values), content=payload, headers=headers)

    assert response.status_code < 500, f"{op.method} {op.path} -> {response.status_code}"
    if response.status_code >= 400:
        body = response.json()
        assert "error_code" in body


@FUZZ_SETTINGS
@given(header=st.one_of(_header_text, st.binary(max_size=100).map(lambda b: b.hex())))
def test_fleet_garbage_api_keys_never_authenticate_or_crash(fleet_fuzz_client, header):
    client, ops, _base = fleet_fuzz_client
    # Pick from this version's own spec — the fleet surface varies by version.
    path = next(op.path for op in ops if op.method == "GET" and "{" not in op.path)
    response = client.get(path, headers={"x-api-key": header})
    assert response.status_code == 401
    assert response.json()["error_code"] == "401"
