#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""Sengkang General Hospital — four care workflows and corridor interruptions.

Based on https://mobile-industrial-robots.com/cases/sengkang-general-hospital
37 MiR250s run four workflows at the Singapore hospital: sterile instrument
delivery to operating theatres, medication rounds from pharmacy, patient meal
delivery, and clean linen distribution. Robots share corridors with beds,
trolleys, and people — interruptions are routine, safety stops are real.

What this exercises on the emulator:
  * a queue of distinct missions (four workflows) draining FIFO
  * /_emulator/faults blocked_path — a bed blocks the corridor mid-mission:
    an active planner error appears while the robot keeps trying to route
    around it; clearing the path clears the error
  * /_emulator/faults emergency_stop — someone hits the red button:
    PUT /status {"clear_error": true} must NOT clear it (matches real MiR),
    only a physical reset (DELETE /_emulator/faults here) releases the robot

Run:
    uv run amr-emulator --mission-duration 3 &
    uv run scenarios/sengkang_hospital_rounds.py
"""

import os
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"

WORKFLOWS = [
    "CSSU: sterile instrument delivery to OT 4",
    "Pharmacy: medication round, wards 5A-5C",
    "Kitchen: patient meal trolley, lunch service",
    "Linen: clean linen distribution, tower B",
]


def client(session: str) -> httpx.Client:
    user = os.environ.get("AMR_USERNAME", "distributor")
    password = os.environ.get("AMR_PASSWORD", "distributor")
    token = robot_token(user, password)
    return httpx.Client(
        base_url=AMR_URL,
        headers={"Authorization": f"Basic {token}", "X-AMR-Session": session},
        timeout=15,
    )


def require_emulator(c: httpx.Client) -> None:
    try:
        index = c.get("/").json()
    except httpx.ConnectError:
        sys.exit(f"Nothing at {AMR_URL} — start one: uv run amr-emulator --mission-duration 3")
    if "emulated_mir_version" not in index:
        sys.exit(f"{AMR_URL} does not look like the emulator; refusing to inject faults into it.")


def status(c: httpx.Client) -> dict:
    return c.get(f"{API}/status").json()


def queue_state(c: httpx.Client, qid: int) -> str:
    return c.get(f"{API}/mission_queue/{qid}").json()["state"]


def wait_for(c: httpx.Client, qid: int, want: str, timeout: float = 60.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if queue_state(c, qid) == want:
            return
        time.sleep(0.2)
    raise TimeoutError(f"queue {qid} never reached {want}")


def main() -> None:
    c = client("sengkang")
    require_emulator(c)
    c.put(f"{API}/status", json={"name": "MiR250-SKH-01"})

    group = c.get(f"{API}/mission_groups").json()[0]["guid"]
    queued = []
    for name in WORKFLOWS:
        guid = c.post(f"{API}/missions", json={"name": name, "group_id": group}).json()["guid"]
        qid = c.post(f"{API}/mission_queue", json={"mission_id": guid}).json()["id"]
        queued.append((name, qid))
    print("morning queue loaded:")
    for name, qid in queued:
        print(f"  [{qid}] {name}")

    # --- Interruption 1: a bed blocks the corridor during the sterile run ---
    sterile_name, sterile_qid = queued[0]
    wait_for(c, sterile_qid, "Executing")
    pos = status(c)["position"]
    c.put("/_emulator/faults", json={"faults": ["blocked_path"]})
    print(f"\n! corridor blocked during '{sterile_name}' at ({pos['x']:.2f}, {pos['y']:.2f})")
    time.sleep(1.5)
    held = status(c)
    errors = [e["description"] for e in held["errors"] if e["code"] != 0]
    if not errors:
        sys.exit("BUG: blocked_path injected but no active error reported")
    # blocked_path is an *active* planner error: the robot keeps trying to
    # route around the bed (still Executing, still moving) while the error
    # stays visible to Fleet and the hospital's middleware.
    print(
        f"  robot keeps trying: state={held['state_text']!r} vel={held['velocity']['linear']}"
        f" pos=({held['position']['x']:.2f}, {held['position']['y']:.2f})"
        f" queue={queue_state(c, sterile_qid)} errors={errors}"
    )
    c.delete("/_emulator/faults")
    print("  porter moves the bed — planner error cleared")
    wait_for(c, sterile_qid, "Done")
    print(f"  [{sterile_qid}] {sterile_name}: Done")

    # --- Interruption 2: emergency stop during the medication round ---
    meds_name, meds_qid = queued[1]
    wait_for(c, meds_qid, "Executing")
    c.put("/_emulator/faults", json={"faults": ["emergency_stop"]})
    print(f"\n! emergency stop pressed during '{meds_name}'")
    stopped = status(c)
    errors = [e["description"] for e in stopped["errors"] if e["code"] != 0]
    print(f"  state={stopped['state_text']!r} errors={errors}")

    c.put(f"{API}/status", json={"clear_error": True})
    after_clear = status(c)
    if after_clear["state_text"] == stopped["state_text"]:
        print("  clear_error via API: correctly refused — an e-stop needs a physical reset")
    else:
        sys.exit("BUG: the API cleared an emergency stop; real MiR firmware never allows that")
    c.delete("/_emulator/faults")
    print("  button reset on the robot — released, mission resumes")
    wait_for(c, meds_qid, "Done")
    print(f"  [{meds_qid}] {meds_name}: Done")

    # --- The rest of the rounds drain normally ---
    print()
    for name, qid in queued[2:]:
        wait_for(c, qid, "Done")
        print(f"  [{qid}] {name}: Done")

    final = status(c)
    level, state = final["battery_percentage"], final["state_text"]
    print(f"\nall four workflows complete; battery {level}%, state {state!r}")


if __name__ == "__main__":
    main()
