"""The MCP 2.0 agent-facing contract, exercised over a real in-process client.

Everything here runs the full protocol — initialize, tools/call,
resources/read, elicitation round-trips, progress notifications — through
``mcp.client.Client`` connected in-memory to the real server module, which
in turn drives the real mir-emulator app over ASGI. No mocks anywhere.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
import pytest
from mcp.client import Client
from mcp.types import ElicitResult, TextContent, TextResourceContents
from mir_emulator.app import create_app
from mir_mcp import client as target_client
from mir_mcp import server

ENV_VARS = (
    "MIR_ROBOT_URL",
    "MIR_FLEET_URL",
    "MIR_USERNAME",
    "MIR_PASSWORD",
    "MIR_API_KEY",
    "MIR_SESSION",
    "MIR_VERSION",
    "MIR_FLEET_VERSION",
)


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, 30))


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    target_client._detected.clear()


@pytest.fixture
def robot(monkeypatch):
    app = create_app("3.8.1", mission_duration=0.2)
    monkeypatch.setattr(target_client, "TRANSPORT", httpx.ASGITransport(app=app))


def _accept(payload: dict[str, Any]):
    async def callback(context, params):
        return ElicitResult(action="accept", content=payload)

    return callback


def _decline():
    async def callback(context, params):
        return ElicitResult(action="decline")

    return callback


def test_initialize_serves_instructions_and_schemas(robot):
    async def scenario():
        async with Client(server.mcp) as session:
            assert "mir_server_info first" in (session.instructions or "")
            tools = (await session.list_tools()).tools
            missing = [t.name for t in tools if not t.output_schema]
            assert not missing, f"tools without output schemas: {missing}"

    run(scenario())


def test_call_tool_returns_structured_content(robot):
    async def scenario():
        async with Client(server.mcp) as session:
            result = await session.call_tool("mir_robot_status", {})
            assert not result.is_error
            doc = result.structured_content
            assert doc["state_text"] == "Ready"
            assert {"x", "y", "orientation"} <= set(doc["position"])

    run(scenario())


def test_tool_failure_uses_the_error_channel(robot):
    async def scenario():
        async with Client(server.mcp) as session:
            result = await session.call_tool("mir_queue_mission", {"mission": "nope"})
            assert result.is_error
            block = result.content[0]
            assert isinstance(block, TextContent)
            text = block.text
            # the message still names what IS available, so the agent recovers
            assert "no mission" in text
            assert "emulated" in text

    run(scenario())


def test_status_resource_reads_live_state(robot):
    async def scenario():
        async with Client(server.mcp) as session:
            listed = await session.list_resources()
            assert server.STATUS_RESOURCE_URI in [str(r.uri) for r in listed.resources]
            read = await session.read_resource(server.STATUS_RESOURCE_URI)
            contents = read.contents[0]
            assert isinstance(contents, TextResourceContents)
            doc = json.loads(contents.text)
            assert doc["state_text"] == "Ready"

    run(scenario())


def test_clearing_the_queue_asks_first_and_honors_decline(robot):
    async def scenario():
        async with Client(server.mcp, elicitation_callback=_decline()) as session:
            await session.call_tool("mir_queue_mission", {"mission": "emulated"})
            result = await session.call_tool("mir_cancel_missions", {})
            assert not result.is_error
            assert result.structured_content["declined"] is True
            queue = await session.call_tool("mir_mission_queue", {})
            assert queue.structured_content["entries"]  # nothing was cancelled

    run(scenario())


def test_clearing_the_queue_proceeds_on_confirmation(robot):
    async def scenario():
        callback = _accept({"confirm": True})
        async with Client(server.mcp, elicitation_callback=callback) as session:
            await session.call_tool("mir_queue_mission", {"mission": "emulated"})
            result = await session.call_tool("mir_cancel_missions", {})
            assert result.structured_content["cancelled"] == "entire mission queue"
            queue = await session.call_tool("mir_mission_queue", {})
            assert queue.structured_content["entries"] == []

    run(scenario())


def test_clients_without_elicitation_keep_the_old_contract(robot):
    """No elicitation capability -> no question, the queue is just cleared."""

    async def scenario():
        async with Client(server.mcp) as session:
            await session.call_tool("mir_queue_mission", {"mission": "emulated"})
            result = await session.call_tool("mir_cancel_missions", {})
            assert result.structured_content["cancelled"] == "entire mission queue"

    run(scenario())


def test_ambiguous_mission_name_elicits_a_choice(robot):
    async def scenario():
        # Create a name collision: a second mission whose name only differs
        # by case, so 'emulated' matches both.
        missions = server._as_list(await server._robot("GET", "/missions"))
        original = next(m for m in missions if m["name"] == "emulated")
        created = await server._robot(
            "POST", "/missions", json_body={"name": "EMULATED", "group_id": "g"}
        )
        chosen = {"guid": created["guid"]}

        seen: list[str] = []

        async def callback(context, params):
            seen.append(params.message)
            return ElicitResult(action="accept", content=chosen)

        async with Client(server.mcp, elicitation_callback=callback) as session:
            result = await session.call_tool("mir_queue_mission", {"mission": "emulated"})
            assert not result.is_error
            assert seen and "matches 2 missions" in seen[0]
            # the elicited guid drove the selection: the queued mission is
            # the created 'EMULATED', not the original 'emulated'
            assert created["guid"] != original["guid"]
            assert result.structured_content["mission"] == "EMULATED"

    run(scenario())


def test_wait_for_reports_progress_and_transitions(robot):
    async def scenario():
        updates: list[str] = []

        async def on_progress(progress: float, total: float | None, message: str | None) -> None:
            updates.append(message or "")

        async with Client(server.mcp) as session:
            await session.call_tool("mir_queue_mission", {"mission": "emulated"})
            result = await session.call_tool(
                "mir_wait_for",
                {"condition": "mission_queue_idle", "timeout_seconds": 20},
                progress_callback=on_progress,
            )
            doc = result.structured_content
            assert doc["met"] is True
            assert doc["status"]["state_text"] == "Ready"
            states = [t["state_text"] for t in doc["transitions"]]
            assert "Executing" in states or len(states) >= 1
            assert updates, "no progress notifications arrived"
            assert any("waiting for mission_queue_idle" in u for u in updates)

    run(scenario())


def test_wait_for_timeout_is_not_an_error(robot):
    async def scenario():
        async with Client(server.mcp) as session:
            result = await session.call_tool(
                "mir_wait_for",
                {"condition": "state_executing", "timeout_seconds": 1},
            )
            doc = result.structured_content
            assert doc["met"] is False
            assert "hint" in doc

    run(scenario())


def test_wait_for_battery_threshold_requires_threshold(robot):
    async def scenario():
        async with Client(server.mcp) as session:
            result = await session.call_tool("mir_wait_for", {"condition": "battery_above"})
            assert result.is_error
            block = result.content[0]
            assert isinstance(block, TextContent)
            assert "threshold" in block.text

    run(scenario())


def test_tools_list_is_marked_cacheable(robot):
    async def scenario():
        async with Client(server.mcp) as session:
            listed = await session.list_tools()
            assert (listed.ttl_ms or 0) > 0

    run(scenario())
