"""Network shaping: X-AMR-Latency delays responses so timeout/retry paths can
be tested. The clamp logic is unit-tested exhaustively; only one small real
delay is measured to prove the sleep actually happens."""

import time

import pytest
from amr_emulator.app import MAX_LATENCY_MS, create_app, parse_latency_ms
from amr_emulator.auth import expected_token
from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app
from starlette.testclient import TestClient

AUTH = {"Authorization": f"Basic {expected_token('distributor', 'distributor')}"}


def test_parse_latency_defaults_and_clamps():
    assert parse_latency_ms(None, 0.0) == 0.0
    assert parse_latency_ms(None, 250.0) == 250.0
    assert parse_latency_ms(None, 10**9) == MAX_LATENCY_MS  # baseline clamps too
    assert parse_latency_ms("0", 500.0) == 0.0  # header overrides baseline
    assert parse_latency_ms("125.5", 0.0) == 125.5
    assert parse_latency_ms(str(10**9), 0.0) == MAX_LATENCY_MS


@pytest.mark.parametrize("bad", ["-1", "nan", "fast", "", "1e999999x", "0x10"])
def test_hostile_latency_headers_are_rejected(bad):
    assert parse_latency_ms(bad, 0.0) is None


def test_invalid_header_is_a_400_not_a_hang():
    client = TestClient(create_app("3.8.1"))
    response = client.get("/api/v2.0.0/status", headers={**AUTH, "X-AMR-Latency": "-5"})
    assert response.status_code == 400
    assert "X-AMR-Latency" in response.json()["error_human"]


def test_header_observably_delays_the_response():
    client = TestClient(create_app("3.8.1"))
    t0 = time.monotonic()
    fast = client.get("/api/v2.0.0/status", headers=AUTH)
    fast_elapsed = time.monotonic() - t0
    assert fast.status_code == 200

    t0 = time.monotonic()
    slow = client.get("/api/v2.0.0/status", headers={**AUTH, "X-AMR-Latency": "150"})
    slow_elapsed = time.monotonic() - t0
    assert slow.status_code == 200
    assert slow_elapsed >= 0.14, f"expected >=140ms, got {slow_elapsed * 1000:.0f}ms"
    assert slow_elapsed > fast_elapsed


def test_baseline_latency_flag_applies_without_header():
    client = TestClient(create_app("3.8.1", latency_ms=120.0))
    t0 = time.monotonic()
    response = client.get("/api/v2.0.0/status", headers=AUTH)
    elapsed = time.monotonic() - t0
    assert response.status_code == 200
    assert elapsed >= 0.11


def test_fleet_honors_the_latency_header_too():
    client = TestClient(create_fleet_app("1.5.0"))
    t0 = time.monotonic()
    response = client.get(
        "/api/v1/system/version",
        headers={"x-api-key": DEFAULT_API_KEY, "X-AMR-Latency": "150"},
    )
    elapsed = time.monotonic() - t0
    assert response.status_code == 200
    assert elapsed >= 0.14


def test_latency_applies_after_auth_so_401s_stay_fast():
    # A rejected caller must not be able to burn worker time with the header.
    client = TestClient(create_app("3.8.1"))
    t0 = time.monotonic()
    response = client.get("/api/v2.0.0/status", headers={"X-AMR-Latency": "5000"})
    elapsed = time.monotonic() - t0
    assert response.status_code == 401
    assert elapsed < 1.0
