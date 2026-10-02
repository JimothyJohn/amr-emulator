"""Boot the real server (uvicorn over TCP) and hit it like a robot client would."""

import socket
import subprocess
import sys
import time

import httpx
import pytest
from amr_emulator import auth

from tests.conftest import ALL_VERSIONS, AUTH_HEADER

pytestmark = pytest.mark.integration


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(params=ALL_VERSIONS, scope="module")
def live_server(request):
    port = _free_port()
    proc = subprocess.Popen(  # noqa: S603 - fixed argv, our own interpreter
        [
            sys.executable,
            "-m",
            "amr_emulator.cli",
            "--mir-version",
            request.param,
            "--port",
            str(port),
        ],
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
        yield request.param, base
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_status_over_real_tcp(live_server):
    _version, base = live_server
    response = httpx.get(f"{base}/api/v2.0.0/status", headers=AUTH_HEADER, timeout=5.0)
    assert response.status_code == 200
    body = response.json()
    assert body["robot_name"] == "MiR_Emulated"
    assert 0 <= body["battery_percentage"] <= 100


def test_auth_enforced_over_real_tcp(live_server):
    _version, base = live_server
    assert httpx.get(f"{base}/api/v2.0.0/status", timeout=5.0).status_code == 401
    bad = {"Authorization": f"Basic {auth.expected_token('admin', 'admin')}"}
    assert httpx.get(f"{base}/api/v2.0.0/status", headers=bad, timeout=5.0).status_code == 401


def test_index_reports_emulated_version(live_server):
    version, base = live_server
    body = httpx.get(f"{base}/", timeout=5.0).json()
    assert body["kind"] == "robot"
    assert body["emulated_mir_version"] == version
    assert body["base_path"] == "/api/v2.0.0"


# connect() warns when the live server's major predates the generated spec —
# expected for the 2.x half of the version matrix.
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_sync_discovery_and_connect_over_real_tcp(live_server):
    """The SDK handshake against a real socket: detect the version the server
    was started with (no client-side pin) and drive it with the result."""
    from amr_client import connect, detect_server
    from amr_client.robot.api.default import get_status

    version, base = live_server
    info = detect_server(base)
    assert (info.kind, info.version) == ("robot", version)
    client = connect(base)
    status = get_status.sync(client=client)
    assert status.state_text == "Ready"


def test_slow_client_cannot_hang_the_server(live_server):
    """Slowloris-ish: an open, silent connection must not block other clients."""
    _version, base = live_server
    host, port = base.removeprefix("http://").split(":")
    lazy = socket.create_connection((host, int(port)), timeout=5)
    try:
        lazy.sendall(b"POST /api/v2.0.0/mission_queue HTTP/1.1\r\nHost: x\r\n")
        start = time.monotonic()
        response = httpx.get(f"{base}/api/v2.0.0/status", headers=AUTH_HEADER, timeout=5.0)
        assert response.status_code == 200
        assert time.monotonic() - start < 5
    finally:
        lazy.close()
