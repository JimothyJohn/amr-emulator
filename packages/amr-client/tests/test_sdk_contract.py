"""The generated SDK against the emulator: the complete dev kit, end to end.

Clients talk over the robot/fleet apps' real HTTP stacks via an in-process
ASGI transport (async-only, so calls go through the generated asyncio API) —
typed models in, typed models out, no sockets.
"""

import asyncio

import httpx
import pytest
from amr_client import fleet_client, provenance, robot_client, robot_token
from amr_emulator.app import create_app
from amr_emulator.fleet import create_fleet_app


def run(coro):
    return asyncio.run(coro)


@pytest.fixture(scope="module")
def robot():
    app = create_app(provenance.ROBOT_VERSION)
    return robot_client("http://robot.test", transport=httpx.ASGITransport(app=app))


@pytest.fixture(scope="module")
def fleet():
    app = create_fleet_app(provenance.FLEET_VERSION)
    return fleet_client("http://fleet.test", transport=httpx.ASGITransport(app=app))


def test_provenance_matches_the_registry():
    from amr_emulator import registry

    assert registry.supported_versions()[0] == provenance.ROBOT_VERSION
    assert registry.fleet_supported_versions()[0] == provenance.FLEET_VERSION
    assert (
        registry.tracked_entry(provenance.ROBOT_VERSION)["sha256"] == provenance.ROBOT_SPEC_SHA256
    )


def test_robot_status_roundtrips_as_a_typed_model(robot):
    from amr_client.robot.api.default import get_status

    status = run(get_status.asyncio(client=robot))
    assert status.state_text == "Ready"
    assert status.battery_percentage == pytest.approx(92.5)
    assert status.robot_model == "MiR250"


def test_robot_auth_is_wired_by_the_constructor(robot):
    from amr_client.robot.api.default import get_status

    response = run(get_status.asyncio_detailed(client=robot))
    assert response.status_code == 200
    # and a client with wrong credentials is rejected by the emulator
    bad = robot_client(
        "http://robot.test",
        password="wrong",
        transport=httpx.ASGITransport(app=create_app(provenance.ROBOT_VERSION)),
    )
    assert run(get_status.asyncio_detailed(client=bad)).status_code == 401


def test_robot_mission_enqueue_via_typed_models(robot):
    from amr_client.robot.api.default import get_mission_queue, get_missions, post_mission_queue
    from amr_client.robot.models import PostMissionQueues

    missions = run(get_missions.asyncio(client=robot))
    entry = run(
        post_mission_queue.asyncio(
            client=robot, body=PostMissionQueues(mission_id=missions[0].guid)
        )
    )
    assert entry.state == "Pending"
    queue = run(get_mission_queue.asyncio(client=robot))
    assert any(item.id == entry.id for item in queue)


def test_fleet_robots_via_typed_models(fleet):
    from amr_client.fleet.api.robot import get_api_v1_robots

    response = run(get_api_v1_robots.asyncio(client=fleet))
    assert len(response.robots) == 2
    assert response.robots[0].name == "MiR_Emulated_1"


def test_fleet_api_key_is_wired_by_the_constructor():
    from amr_client.fleet.api.robot import get_api_v1_robots

    bad = fleet_client(
        "http://fleet.test",
        api_key="wrong",
        transport=httpx.ASGITransport(app=create_fleet_app(provenance.FLEET_VERSION)),
    )
    assert run(get_api_v1_robots.asyncio_detailed(client=bad)).status_code == 401


def test_robot_token_matches_the_emulator_expectation():
    from amr_emulator.auth import expected_token

    assert robot_token() == expected_token("distributor", "distributor")


@pytest.mark.integration
def test_generated_sdk_matches_the_registry_no_drift():
    """Regenerates into a temp dir; any diff means someone hand-edited the
    generated tree or the registry moved without regeneration."""
    import subprocess
    import sys
    from pathlib import Path

    script = Path(__file__).resolve().parents[3] / "scripts" / "generate_client.py"
    result = subprocess.run(  # noqa: S603 - our own script, fixed args
        [sys.executable, str(script), "--check"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
