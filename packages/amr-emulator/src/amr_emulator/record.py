"""Scenario record & replay: capture a request sequence, replay it as a test.

Recording is per virtual robot (so per session): PUT /_emulator/recorder
{"recording": true} starts capturing every API request/response pair that
robot (or fleet) serves, together with the simulation-clock instant it
happened at. GET returns the scenario as JSON; save it to a file.

Replay rebuilds a FRESH emulator of the same version and plays the steps
back with the clock frozen to each recorded instant. Because the whole
mission simulation is time-derived, this makes replay byte-identical — the
recorded battery, positions, and lifecycle timestamps all reproduce exactly.
A step whose live response differs from the recording is a regression.

Replay assumes the scenario was recorded against the default credentials
(it replays with them) and mutates the module clock while running — call it
from one thread at a time, like any clock-freezing test.
"""

from __future__ import annotations

from typing import Any

from amr_emulator import behaviors
from amr_emulator.state import StateStore

SCENARIO_FORMAT = 1
MAX_STEPS = 2000
RECORDER_KEY = "/recorder"


def recorder_state(state: StateStore) -> dict:
    return state.singleton(RECORDER_KEY, {"recording": False, "steps": []})


def set_recording(state: StateStore, recording: bool) -> None:
    recorder_state(state)["recording"] = bool(recording)


def clear_recording(state: StateStore) -> None:
    doc = recorder_state(state)
    doc["recording"] = False
    doc["steps"] = []


def record_step(
    state: StateStore,
    *,
    method: str,
    path: str,
    query: str,
    body: Any,
    status: int,
    payload: Any,
    media_type: str,
) -> None:
    doc = recorder_state(state)
    if not doc.get("recording") or len(doc["steps"]) >= MAX_STEPS:
        return
    doc["steps"].append(
        {
            "at": behaviors._now(),
            "method": method,
            "path": path,
            "query": query,
            "body": body,
            "status": status,
            "response": payload,
            "media_type": media_type,
        }
    )


def scenario_doc(state: StateStore, *, version: str, family: str) -> dict:
    doc = recorder_state(state)
    return {
        "amr_emulator_scenario": SCENARIO_FORMAT,
        "family": family,
        "version": version,
        "recording": doc.get("recording", False),
        "steps": list(doc["steps"]),
    }


def replay(scenario: dict) -> list[str]:
    """Replay *scenario* against a fresh emulator; return the mismatches.

    An empty list means every step reproduced byte-identically.
    """
    from starlette.testclient import TestClient

    from amr_emulator.auth import DEFAULT_PASSWORD, DEFAULT_USERNAME, expected_token

    if scenario.get("amr_emulator_scenario") != SCENARIO_FORMAT:
        return ["not a amr-emulator scenario (or unsupported format version)"]
    steps = scenario.get("steps") or []
    if not steps:
        return ["scenario has no steps"]

    family = scenario.get("family", "robot")
    version = scenario.get("version", "")
    if family == "fleet":
        from amr_emulator.fleet import DEFAULT_API_KEY, create_fleet_app

        app = create_fleet_app(version)
        headers = {"x-api-key": DEFAULT_API_KEY}
    else:
        from amr_emulator.app import create_app

        app = create_app(version)
        headers = {"Authorization": f"Basic {expected_token(DEFAULT_USERNAME, DEFAULT_PASSWORD)}"}

    problems: list[str] = []
    frozen = {"now": float(steps[0]["at"])}

    def _frozen_now() -> float:
        return frozen["now"]

    original_now = behaviors._now
    behaviors._now = _frozen_now  # replay owns the clock
    try:
        client = TestClient(app, raise_server_exceptions=False)
        for index, step in enumerate(steps):
            frozen["now"] = float(step["at"])
            label = f"step {index}: {step['method']} {step['path']}"
            response = client.request(
                step["method"],
                step["path"] + (f"?{step['query']}" if step.get("query") else ""),
                headers=headers,
                json=step["body"] if step.get("body") is not None else None,
            )
            if response.status_code != step["status"]:
                problems.append(
                    f"{label}: status {response.status_code} != recorded {step['status']}"
                )
                continue
            if "json" in step.get("media_type", "application/json"):
                try:
                    live: Any = response.json() if response.content else None
                except ValueError:
                    live = response.text
            else:
                live = response.text
            if live != step["response"]:
                problems.append(f"{label}: response body differs from the recording")
    finally:
        behaviors._now = original_now
    return problems
