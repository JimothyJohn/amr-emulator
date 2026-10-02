"""The /_emulator/ws/status push channel: auth, session isolation, live state."""

import pytest
from amr_emulator import behaviors
from amr_emulator.app import create_app
from amr_emulator.auth import expected_token
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

TOKEN = expected_token("distributor", "distributor")
AUTH = {"Authorization": f"Basic {TOKEN}"}
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
def client():
    return TestClient(create_app("3.8.1"))


def test_ws_pushes_the_status_document(client):
    with client.websocket_connect(f"/_emulator/ws/status?token={TOKEN}&interval=0.1") as ws:
        doc = ws.receive_json()
    assert doc["state_text"] == "Ready"
    assert "battery_percentage" in doc


def test_ws_rejects_missing_and_bad_tokens(client):
    for url in ("/_emulator/ws/status", "/_emulator/ws/status?token=bogus"):
        with pytest.raises(WebSocketDisconnect) as exc, client.websocket_connect(url):
            pass
        assert exc.value.code == 4401


def test_ws_header_auth_also_works(client):
    with client.websocket_connect("/_emulator/ws/status?interval=0.1", headers=AUTH) as ws:
        assert ws.receive_json()["state_text"] == "Ready"


def test_ws_reflects_live_mission_state(clock, client):
    mission = client.get("/api/v2.0.0/missions", headers=AUTH).json()[0]["guid"]
    client.post("/api/v2.0.0/mission_queue", headers=AUTH, json={"mission_id": mission})
    clock.tick(2.0)
    with client.websocket_connect(f"/_emulator/ws/status?token={TOKEN}&interval=0.1") as ws:
        doc = ws.receive_json()
    assert doc["state_text"] == "Executing"


def test_ws_honors_session_isolation(clock, client):
    session = {**AUTH, "X-AMR-Session": "crew-a"}
    mission = client.get("/api/v2.0.0/missions", headers=session).json()[0]["guid"]
    client.post("/api/v2.0.0/mission_queue", headers=session, json={"mission_id": mission})
    clock.tick(2.0)
    with client.websocket_connect(
        f"/_emulator/ws/status?token={TOKEN}&session=crew-a&interval=0.1"
    ) as ws:
        in_session = ws.receive_json()
    with client.websocket_connect(f"/_emulator/ws/status?token={TOKEN}&interval=0.1") as ws:
        default = ws.receive_json()
    assert in_session["state_text"] == "Executing"
    assert default["state_text"] == "Ready"


def test_ws_rejects_invalid_session_and_interval(client):
    for url in (
        f"/_emulator/ws/status?token={TOKEN}&session=bad session!",
        f"/_emulator/ws/status?token={TOKEN}&interval=fast",
    ):
        with pytest.raises(WebSocketDisconnect) as exc, client.websocket_connect(url):
            pass
        assert exc.value.code == 4400
