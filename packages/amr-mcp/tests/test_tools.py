"""amr-mcp tool tests against real emulator apps over in-process ASGI.

No mocked services: every test drives the actual amr-emulator application
(robot or fleet) through the same HTTP stack production uses, with the MCP
tools' own auth derivation. Contract under test: natural-language-shaped
inputs -> documented MiR API effects -> readable JSON/error strings out.
"""

from __future__ import annotations

import asyncio
import socket
import threading
import time
from contextlib import closing
from typing import Any

import httpx
import pytest
import uvicorn
from amr_emulator.app import create_app
from amr_emulator.fleet import create_fleet_app
from amr_mcp import client, server
from mcp.server.mcpserver.exceptions import ToolError

ENV_VARS = (
    "AMR_ROBOT_URL",
    "AMR_FLEET_URL",
    "AMR_USERNAME",
    "AMR_PASSWORD",
    "AMR_API_KEY",
    "AMR_SESSION",
    "AMR_VERSION",
    "AMR_FLEET_VERSION",
)


def run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    # Discovery results are cached per base URL; tests swap the transport
    # under the same URL, so every test starts with a cold handshake.
    client._detected.clear()


@pytest.fixture
def robot(monkeypatch):
    app = create_app("3.8.1", mission_duration=0.2)
    monkeypatch.setattr(client, "TRANSPORT", httpx.ASGITransport(app=app))


@pytest.fixture
def fleet(monkeypatch):
    app = create_fleet_app("1.5.0", mission_duration=0.2)
    monkeypatch.setattr(client, "TRANSPORT", httpx.ASGITransport(app=app))


def test_every_tool_is_registered():
    tools = {t.name for t in run(server.mcp.list_tools())}
    assert tools == {
        "amr_server_info",
        "amr_discover_robots",
        "amr_robot_status",
        "amr_set_robot_state",
        "amr_clear_error",
        "amr_list_missions",
        "amr_queue_mission",
        "amr_mission_queue",
        "amr_cancel_missions",
        "amr_read_register",
        "amr_write_register",
        "amr_manage_faults",
        "amr_fleet_robots",
        "amr_fleet_dispatch",
        "amr_fleet_order_status",
        "amr_generate_report",
        "amr_wait_for",
    }


def test_status_reports_live_state(robot):
    doc = run(server.amr_robot_status())
    assert doc["state_text"] == "Ready"
    assert 0 <= doc["battery_percentage"] <= 100
    assert {"x", "y", "orientation"} <= set(doc["position"])


def test_pause_then_resume_round_trip(robot):
    paused = run(server.amr_set_robot_state("pause"))
    assert paused["state_id"] == 4
    ready = run(server.amr_set_robot_state("ready"))
    assert ready["state_id"] == 3


def test_queue_mission_by_case_insensitive_name_and_wait(robot):
    result = run(server.amr_queue_mission("EMULATED", wait_seconds=10))
    assert result["mission"] == "emulated"
    assert result["queue_entry"]["state"] == "Done"


def test_queue_mission_by_guid(robot):
    missions = run(server.amr_list_missions())["missions"]
    result = run(server.amr_queue_mission(missions[0]["guid"]))
    assert result["queue_entry"]["state"] in ("Pending", "Executing")


def test_queue_unknown_mission_lists_alternatives(robot):
    with pytest.raises(ToolError, match="no mission") as err:
        run(server.amr_queue_mission("take-over-the-world"))
    assert "emulated" in str(err.value)  # tells the agent what IS available


def test_cancel_whole_queue(robot):
    run(server.amr_queue_mission("emulated"))
    assert run(server.amr_cancel_missions())["cancelled"] == "entire mission queue"
    assert run(server.amr_mission_queue())["entries"] == []


def test_register_write_read_round_trip(robot):
    written = run(server.amr_write_register(7, 42))
    assert float(written["value"]) == 42
    read = run(server.amr_read_register(7))
    assert float(read["value"]) == 42


def test_register_out_of_range_is_an_error(robot):
    with pytest.raises(ToolError):
        run(server.amr_read_register(999))


def test_fault_injection_and_recovery(robot):
    injected = run(server.amr_manage_faults(["emergency_stop"]))
    assert injected["active"] == ["emergency_stop"]
    assert run(server.amr_robot_status())["state_text"] == "EmergencyStop"
    # clear_error must NOT clear an e-stop (matches real MiR behavior)...
    run(server.amr_clear_error())
    assert run(server.amr_robot_status())["state_text"] == "EmergencyStop"
    # ...but the emulator-only fault surface clears everything.
    cleared = run(server.amr_manage_faults())
    assert cleared["active"] == []
    assert run(server.amr_robot_status())["state_text"] == "Ready"


def test_wrong_password_yields_actionable_401(robot, monkeypatch):
    monkeypatch.setenv("AMR_PASSWORD", "not-the-password")
    with pytest.raises(ToolError) as err:
        run(server.amr_robot_status())
    assert "401" in str(err.value)
    assert "AMR_USERNAME" in str(err.value)  # points at the fix, not just the failure


def test_unreachable_robot_says_how_to_start_one(monkeypatch):
    monkeypatch.setattr(client, "TRANSPORT", None)
    monkeypatch.setenv("AMR_ROBOT_URL", "http://127.0.0.1:9")  # discard port: refuses fast
    with pytest.raises(ToolError, match="cannot reach") as err:
        run(server.amr_robot_status())
    assert "amr-emulator" in str(err.value)


def test_fleet_lists_embedded_robots(fleet):
    doc = run(server.amr_fleet_robots())
    robots = doc["robots"]
    assert len(robots) == 2
    one = run(server.amr_fleet_robots(robots[0]["robot-id"]))
    assert one["robot-identity"]["robot-id"] == robots[0]["robot-id"]


def test_fleet_dispatch_by_name_then_track_and_abort(fleet):
    order = run(server.amr_fleet_dispatch(["EMULATED", "emulated"]))
    serial_id = order["id"]
    status = run(server.amr_fleet_order_status(serial_id))
    assert len(status["phases"]) == 2
    aborted = run(server.amr_fleet_order_status(serial_id, abort=True))
    assert aborted == {"aborted": serial_id}


def test_fleet_dispatch_unknown_mission_is_atomic(fleet):
    with pytest.raises(ToolError, match="no site mission matches"):
        run(server.amr_fleet_dispatch(["emulated", "no-such-mission"]))
    # nothing was dispatched: the fleet has no orders
    assert run(server._fleet("GET", "/order")) == []


def test_fleet_wrong_api_key_is_actionable(fleet, monkeypatch):
    monkeypatch.setenv("AMR_API_KEY", "wrong")
    with pytest.raises(ToolError, match="AMR_API_KEY"):
        run(server.amr_fleet_robots())


# ------------------------------------------------- connect-time discovery


@pytest.fixture
def dispatcher(monkeypatch):
    """The multi-version demo dispatcher at the configured base URL."""
    from amr_emulator.serverless import build_app

    monkeypatch.setattr(client, "TRANSPORT", httpx.ASGITransport(app=build_app()))


def test_server_info_identifies_a_robot(robot):
    doc = run(server.amr_server_info())
    assert doc["robot_target"]["kind"] == "robot"
    assert doc["robot_target"]["software_version"] == "3.8.1"
    assert "fleet_target" not in doc  # same URL, and it is not fleet-shaped


def test_server_info_identifies_a_fleet(fleet):
    doc = run(server.amr_server_info())
    assert doc["robot_target"]["kind"] == "fleet"
    assert doc["fleet_target"]["software_version"] == "1.5.0"


def test_tools_work_against_a_dispatcher_root_without_a_version(dispatcher):
    """The headline: point AMR_ROBOT_URL at the multi-version demo root and
    every tool adapts — no version installed, configured, or guessed."""
    from amr_emulator import registry

    doc = run(server.amr_robot_status())
    assert doc["state_text"] == "Ready"
    info = run(server.amr_server_info())
    latest = registry.supported_versions()[0]
    assert info["robot_target"]["kind"] == "dispatcher"
    assert info["robot_target"]["resolved_base"].endswith(f"/{latest}")
    assert info["robot_target"]["available_versions"] == registry.supported_versions()
    # and the fleet side resolves its own newest mount
    robots = run(server.amr_fleet_robots())
    assert len(robots["robots"]) == 2


def test_dispatcher_version_pin_is_honored(dispatcher, monkeypatch):
    from amr_emulator import registry

    oldest = registry.supported_versions()[-1]
    monkeypatch.setenv("AMR_VERSION", oldest)
    info = run(server.amr_server_info())
    assert info["robot_target"]["resolved_base"].endswith(f"/{oldest}")
    doc = run(server.amr_robot_status())
    assert doc["state_text"] == "Ready"


def test_dispatcher_rejects_an_unserved_version_pin(dispatcher, monkeypatch):
    monkeypatch.setenv("AMR_VERSION", "9.9.9")
    with pytest.raises(ToolError, match=r"AMR_VERSION=9\.9\.9 is not served"):
        run(server.amr_robot_status())
    info = run(server.amr_server_info())
    assert info["robot_target"]["error"].startswith("Error: AMR_VERSION=9.9.9")


def test_handshake_runs_once_per_base_url(robot, monkeypatch):
    """The probe is a connect-time cost, not a per-request tax."""
    calls: list[str] = []
    original = client._identify

    async def counting(base_url: str) -> dict[str, Any] | None:
        calls.append(base_url)
        return await original(base_url)

    monkeypatch.setattr(client, "_identify", counting)
    run(server.amr_robot_status())
    run(server.amr_robot_status())
    assert len(calls) == 1


def test_unreachable_target_reports_unknown_kind(monkeypatch):
    class Down(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            raise httpx.ConnectError("down", request=request)

    monkeypatch.setattr(client, "TRANSPORT", Down())
    info = run(server.amr_server_info())
    assert info["robot_target"]["kind"] == "unknown"
    assert "note" in info["robot_target"]


# ------------------------------------------------- network discovery (amr_discover_robots)


class _LiveApp:
    """Serve an ASGI app on a real ephemeral port for a scan to find."""

    def __init__(self, app):
        with closing(socket.socket()) as s:
            s.bind(("127.0.0.1", 0))
            self.port = s.getsockname()[1]
        cfg = uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning")
        self._server = uvicorn.Server(cfg)
        self._thread = threading.Thread(target=self._server.run, daemon=True)

    def __enter__(self) -> int:
        self._thread.start()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self._server.started:
                return self.port
            time.sleep(0.02)
        raise RuntimeError("uvicorn did not start")

    def __exit__(self, *exc) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=10)


def test_discover_finds_a_robot_by_ip(monkeypatch):
    # A real network scan uses real sockets, not the injected ASGI transport.
    monkeypatch.setattr(client, "TRANSPORT", None)
    with _LiveApp(create_app("3.8.1")) as port:
        # Point the scan's port list at the robot's real ephemeral port.
        monkeypatch.setattr(client, "SCAN_PORTS", (port,))
        doc = run(server.amr_discover_robots(["127.0.0.1"]))
    assert doc["count"] == 1
    got = doc["found"][0]
    assert got["kind"] == "robot"
    assert got["version"] == "3.8.1"
    assert got["url"] == f"http://127.0.0.1:{port}"


def test_discover_ignores_a_non_mir_server(monkeypatch):
    monkeypatch.setattr(client, "TRANSPORT", None)

    class Hello:
        async def __call__(self, scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b'{"hello":"world"}'})

    with _LiveApp(Hello()) as port:
        monkeypatch.setattr(client, "SCAN_PORTS", (port,))
        doc = run(server.amr_discover_robots(["127.0.0.1"]))
    assert doc["found"] == []


def test_discover_empty_host_list_is_actionable(monkeypatch):
    monkeypatch.setattr(client, "TRANSPORT", None)
    with pytest.raises(ToolError, match="no hosts to scan"):
        run(server.amr_discover_robots([]))


def test_discover_rejects_an_oversized_sweep(monkeypatch):
    monkeypatch.setattr(client, "TRANSPORT", None)
    with pytest.raises(ToolError, match="exceeds"):
        run(server.amr_discover_robots(["10.0.0.0/16"]))


def test_generate_report_writes_a_robot_dashboard(robot, tmp_path):
    out = tmp_path / "report.html"
    result = run(server.amr_generate_report(str(out)))
    assert result["kind"] == "robot"
    assert result["path"] == str(out)
    assert result["robots"] and 0 <= result["robots"][0]["battery"] <= 100
    html = out.read_text()
    assert html.startswith("<!DOCTYPE html>")
    # "Timeline" became the collapsed "Event log" when the dashboard
    # moved to the shift-KPI layout (amr-client report.py).
    for section in ("Current status", "Daily trend", "Event log"):
        assert section in html, section


def test_generate_report_writes_a_fleet_dashboard(fleet, tmp_path):
    out = tmp_path / "fleet.html"
    result = run(server.amr_generate_report(str(out), target="fleet"))
    assert result["kind"] == "fleet"
    assert len(result["robots"]) == 2
    assert "MiR_Emulated_1" in out.read_text()


def test_generate_report_unreachable_target_is_an_error(monkeypatch, tmp_path):
    monkeypatch.setenv("AMR_ROBOT_URL", "http://127.0.0.1:1")  # nothing listens
    with pytest.raises(ToolError):
        run(server.amr_generate_report(str(tmp_path / "x.html")))
    assert not (tmp_path / "x.html").exists()


def test_as_list_accepts_both_declared_shapes():
    # MiR specs declare some list endpoints with the element's object schema;
    # a single-object answer is one entry, never silently nothing.
    assert server._as_list([{"guid": "a"}]) == [{"guid": "a"}]
    assert server._as_list({"guid": "a"}) == [{"guid": "a"}]
    assert server._as_list(None) == []
    assert server._as_list("Error: nope") == []
