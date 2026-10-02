#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""FM Logistic — "Mirek" runs the recycling loop, shift after shift.

Based on https://mobile-industrial-robots.com/cases/fm-logistic
One MiR200 (the crew named it Mirek) hauls used cardboard from a co-packing
line to a recycling tippler: 300 m per mission in ~10.5 minutes, 18.5 km a
day, three shifts, ~200 tons of packaging a year. The interesting part of a
one-robot deployment is endurance: odometry, battery, and knowing when to
stop for a charge.

What this exercises on the emulator:
  * back-to-back mission cycles on one robot
  * X-AMR-Mission-Duration — the loaded 300 m haul runs 3x longer than the
    empty return, in the same FIFO queue; odometry and drain scale with it
  * `moved` odometry and `battery_percentage` deltas per cycle
  * a low-battery guard (stop dispatching below a threshold)
  * GET /metrics — the OpenMetrics endpoint a Prometheus stack would
    scrape, including the mission completed/aborted counters

Run:
    uv run amr-emulator --mission-duration 2 &
    uv run scenarios/fm_logistic_endurance.py         # CYCLES=5 by default
"""

import os
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"
CYCLES = int(os.environ.get("CYCLES", "5"))
MIN_BATTERY = 20.0  # % — hold dispatch below this, like Fleet would
HAUL_S = "6"  # loaded 300 m run (X-AMR-Mission-Duration, emulator-only)
RETURN_S = "2"  # empty run back to the co-packing line


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
        sys.exit(f"Nothing at {AMR_URL} — start one: uv run amr-emulator --mission-duration 2")
    if "emulated_mir_version" not in index:
        sys.exit(f"{AMR_URL} does not look like the emulator; refusing to run a demo against it.")


def status(c: httpx.Client) -> dict:
    return c.get(f"{API}/status").json()


def main() -> None:
    c = client("fm-logistic")
    require_emulator(c)
    c.put(f"{API}/status", json={"name": "Mirek"})

    group = c.get(f"{API}/mission_groups").json()[0]["guid"]
    mission = c.post(
        f"{API}/missions",
        json={"name": "Recycling run: co-packing line -> tippler", "group_id": group},
    ).json()["guid"]

    s = status(c)
    name, level, odo = s["robot_name"], s["battery_percentage"], s["moved"]
    print(f"{name} on shift: battery {level}%, odometer {odo:.1f} m\n")
    total_m = total_pct = 0.0

    for cycle in range(1, CYCLES + 1):
        before = status(c)
        level = before["battery_percentage"]
        if level < MIN_BATTERY:
            print(f"battery {level}% < {MIN_BATTERY}% — holding dispatch, send it to charge")
            break
        # Loaded hauls outlast empty returns — alternate them so the same
        # FIFO queue carries two different per-mission durations.
        loaded = cycle % 2 == 1
        duration = HAUL_S if loaded else RETURN_S
        t0 = time.monotonic()
        qid = c.post(
            f"{API}/mission_queue",
            json={"mission_id": mission},
            headers={"X-AMR-Mission-Duration": duration},
        ).json()["id"]
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if c.get(f"{API}/mission_queue/{qid}").json()["state"] == "Done":
                break
            time.sleep(0.2)
        else:
            sys.exit(f"cycle {cycle} never finished")
        after = status(c)
        meters = after["moved"] - before["moved"]
        drained = before["battery_percentage"] - after["battery_percentage"]
        total_m += meters
        total_pct += drained
        leg = "loaded haul " if loaded else "empty return"
        print(
            f"cycle {cycle} ({leg}): {meters:6.1f} m in {time.monotonic() - t0:4.1f}s, "
            f"battery -{drained:.2f}% (now {after['battery_percentage']:.2f}%)"
        )

    print(
        f"\nshift summary: {total_m:.1f} m travelled, {total_pct:.2f}% battery over {CYCLES} runs"
    )
    if total_pct > 0:
        km_per_charge = total_m / total_pct * 100 / 1000
        print(f"projected range: ~{km_per_charge:.1f} km per charge (Mirek's real day is 18.5 km)")

    print("\nwhat the monitoring stack sees (GET /metrics):")
    for line in c.get(f"{API}/metrics").text.splitlines():
        if line and not line.startswith("#"):
            print(f"  {line}")


if __name__ == "__main__":
    main()
