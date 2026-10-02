#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""Novo Nordisk Tianjin — a crowded 100 m route and a congested network.

Based on https://mobile-industrial-robots.com/cases/novo-nordisk-china
Five MiR500s move packaging material from depot to high-bay storage on a
100 m route with 3-4 turns through the busiest part of the plant. The
robots slow, stop, and reroute around people and forklifts; the deployment
saved 35+ hours of forklift time a week. Busy plants also mean busy Wi-Fi —
a resilient client has to survive slow responses.

What this exercises on the emulator:
  * /_emulator/faults blocked_path mid-mission — a forklift crosses the
    aisle; an active planner error appears while the robot keeps trying,
    and clearing the path clears the error
  * X-AMR-Latency — per-request response delay to prove your client's
    timeout-and-retry path actually works before you meet real plant Wi-Fi

Run:
    uv run amr-emulator --mission-duration 3 &
    uv run scenarios/novo_nordisk_crowded_route.py
"""

import os
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"


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


def main() -> None:
    c = client("novo-nordisk")
    require_emulator(c)
    c.put(f"{API}/status", json={"name": "MiR500-NN-03"})

    group = c.get(f"{API}/mission_groups").json()[0]["guid"]
    mission = c.post(
        f"{API}/missions",
        json={
            "name": "Packaging material: depot -> high-bay storage (100 m, 4 turns)",
            "group_id": group,
        },
    ).json()["guid"]

    qid = c.post(f"{API}/mission_queue", json={"mission_id": mission}).json()["id"]
    print(f"mission queued [{qid}]: depot -> high-bay through the busy aisle")

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if c.get(f"{API}/mission_queue/{qid}").json()["state"] == "Executing":
            break
        time.sleep(0.2)

    # A forklift crosses the aisle. blocked_path raises an *active* planner
    # error — the robot slows, reroutes, keeps trying (exactly the behavior
    # Novo Nordisk describes) — rather than freezing like an e-stop.
    c.put("/_emulator/faults", json={"faults": ["blocked_path"]})
    held = status(c)
    errors = [e["description"] for e in held["errors"] if e["code"] != 0]
    if not errors:
        sys.exit("BUG: blocked_path injected but no active error reported")
    pos = held["position"]
    print(
        f"! forklift in the aisle: state={held['state_text']!r} "
        f"vel={held['velocity']['linear']} pos=({pos['x']:.2f}, {pos['y']:.2f}) errors={errors}"
    )
    time.sleep(1.5)
    pos = status(c)["position"]
    mission_state = c.get(f"{API}/mission_queue/{qid}").json()["state"]
    print(
        f"  1.5s later: still trying, pos=({pos['x']:.2f}, {pos['y']:.2f}), mission {mission_state}"
    )
    c.delete("/_emulator/faults")
    cleared = [e["description"] for e in status(c)["errors"] if e["code"] != 0]
    print(f"  aisle clear — errors now {cleared}")

    while time.monotonic() < deadline:
        if c.get(f"{API}/mission_queue/{qid}").json()["state"] == "Done":
            break
        time.sleep(0.2)
    print(f"mission [{qid}] Done; pallet on the high-bay rack\n")

    # Busy plant Wi-Fi: the same GET /status with 2s of injected latency
    # against a 1s client timeout. First attempt must fail; the retry
    # (patient timeout, no injected latency) must succeed.
    print("network resilience drill (X-AMR-Latency=2000 vs timeout=1.0):")
    try:
        c.get(f"{API}/status", headers={"X-AMR-Latency": "2000"}, timeout=1.0)
        sys.exit("BUG: a 2s-delayed response beat a 1s timeout")
    except httpx.TimeoutException:
        print("  attempt 1: timed out as designed — client survives, no crash")
    s = status(c)
    print(
        f"  attempt 2 (retry): {s['state_text']!r}, battery {s['battery_percentage']}% — recovered"
    )
    print("\nReal-world reference: 5 MiR500s, 35+ forklift-hours saved weekly on this route.")


if __name__ == "__main__":
    main()
