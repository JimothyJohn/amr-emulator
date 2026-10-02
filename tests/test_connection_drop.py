"""connection_drop fault over a real TCP server: in-flight API requests die
with a transport error — never an HTTP status — exactly the failure shape a
rebooting robot produces. The /_emulator/* surfaces stay reachable so the
fault can be cleared without restarting anything.

Real uvicorn over TCP (integration marker): in-process ASGI clients cannot
model a severed socket.
"""

import socket
import subprocess
import sys
import time

import httpx
import pytest

from tests.conftest import ALL_VERSIONS, AUTH_HEADER

pytestmark = pytest.mark.integration

VERSION = ALL_VERSIONS[0]  # transport behavior is version-blind


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def live_server():
    port = _free_port()
    proc = subprocess.Popen(  # noqa: S603 - fixed argv, our own interpreter
        [sys.executable, "-m", "amr_emulator.cli", "--mir-version", VERSION, "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                out = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
                pytest.fail(f"emulator exited early:\n{out}")
            try:
                httpx.get(base + "/", timeout=1.0)
                break
            except httpx.TransportError:
                time.sleep(0.1)
        else:
            pytest.fail("emulator did not come up within 15s")
        yield base
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_connection_drop_severs_api_requests_and_clears(live_server):
    base = live_server
    healthy = httpx.get(f"{base}/api/v2.0.0/status", headers=AUTH_HEADER, timeout=5)
    assert healthy.status_code == 200

    armed = httpx.put(
        f"{base}/_emulator/faults",
        json={"faults": ["connection_drop"]},
        headers=AUTH_HEADER,
        timeout=5,
    )
    assert armed.status_code == 200

    # a transport error, not an HTTP status — reads and writes alike
    with pytest.raises(httpx.TransportError):
        httpx.get(f"{base}/api/v2.0.0/status", headers=AUTH_HEADER, timeout=5)
    with pytest.raises(httpx.TransportError):
        httpx.post(
            f"{base}/api/v2.0.0/mission_queue",
            json={"mission_id": "whatever"},
            headers=AUTH_HEADER,
            timeout=5,
        )

    # the emulator surface survives: clear the fault, the API recovers
    cleared = httpx.delete(f"{base}/_emulator/faults", headers=AUTH_HEADER, timeout=5)
    assert cleared.status_code == 200
    recovered = httpx.get(f"{base}/api/v2.0.0/status", headers=AUTH_HEADER, timeout=5)
    assert recovered.status_code == 200


def test_connection_drop_is_session_isolated(live_server):
    base = live_server
    httpx.put(
        f"{base}/_emulator/faults",
        json={"faults": ["connection_drop"]},
        headers={**AUTH_HEADER, "X-AMR-Session": "rebooting"},
        timeout=5,
    )
    try:
        with pytest.raises(httpx.TransportError):
            httpx.get(
                f"{base}/api/v2.0.0/status",
                headers={**AUTH_HEADER, "X-AMR-Session": "rebooting"},
                timeout=5,
            )
        untouched = httpx.get(
            f"{base}/api/v2.0.0/status",
            headers={**AUTH_HEADER, "X-AMR-Session": "healthy"},
            timeout=5,
        )
        assert untouched.status_code == 200
    finally:
        httpx.delete(
            f"{base}/_emulator/faults",
            headers={**AUTH_HEADER, "X-AMR-Session": "rebooting"},
            timeout=5,
        )
