#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""Whirlpool Łódź — line-side delivery loop with a hot-spare robot.

Based on https://mobile-industrial-robots.com/cases/whirlpool
Three MiR200s shuttle 12 dryer doors per run on a ~130 m loop between
preassembly and the assembly line (~3 min 50 s per cycle). Two robots run
missions while the third waits on the charger as a hot spare; MiR Fleet
watches batteries and rotates robots.

What this exercises on the emulator:
  * X-AMR-Session — three fully isolated robots on one emulator
  * PUT /status {"name": ...} — naming robots
  * POST /missions + POST /mission_queue — per-robot mission definitions
  * X-AMR-Mission-Duration — the 130 m loop outlasts the global default
  * battery drain across repeated cycles + spare rotation on low battery,
    with the spare genuinely recharging on /_emulator/battery — the swap
    is a real trade, not theater

Run:
    uv run amr-emulator --mission-duration 2 &
    uv run scenarios/whirlpool_lineside_loop.py
"""

import os
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"
CYCLES = 4
ROTATE_BELOW = 99.0  # % — artificially high so the demo shows a rotation
LOOP_DURATION_S = "4"  # the 130 m loop takes longer than the global default
CHARGE_RATE = 0.25  # %/s on the charger — visibly outpaces the loop's drain


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


def make_mission(c: httpx.Client, name: str) -> str:
    group = c.get(f"{API}/mission_groups").json()[0]["guid"]
    r = c.post(f"{API}/missions", json={"name": name, "group_id": group})
    r.raise_for_status()
    return r.json()["guid"]


def run_mission(c: httpx.Client, guid: str) -> int:
    r = c.post(
        f"{API}/mission_queue",
        json={"mission_id": guid},
        headers={"X-AMR-Mission-Duration": LOOP_DURATION_S},
    )
    r.raise_for_status()
    return r.json()["id"]


def set_charging(c: httpx.Client, on: bool) -> None:
    body = {"charging": True, "charge_rate": CHARGE_RATE} if on else {"charging": False}
    c.put("/_emulator/battery", json=body).raise_for_status()


def wait_done(c: httpx.Client, queue_id: int, timeout: float = 60.0) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = c.get(f"{API}/mission_queue/{queue_id}").json()["state"]
        if state in ("Done", "Aborted"):
            return state
        time.sleep(0.3)
    raise TimeoutError(f"queue entry {queue_id} not finished after {timeout}s")


def battery(c: httpx.Client) -> float:
    return c.get(f"{API}/status").json()["battery_percentage"]


def main() -> None:
    robots = {}
    for n in (1, 2, 3):
        c = client(f"whirlpool-amr-{n}")
        require_emulator(c)
        c.put(f"{API}/status", json={"name": f"MiR200-{n}"})
        robots[n] = {
            "client": c,
            "mission": make_mission(c, "Line-side loop: 12 dryer doors, preassembly -> line"),
        }

    active, spare = [1, 2], 3
    set_charging(robots[spare]["client"], True)  # the hot spare sits on the charger
    print(f"fleet up: robots 1-3, active={active}, hot spare={spare} (on charger)\n")

    for cycle in range(1, CYCLES + 1):
        queued = [(n, run_mission(robots[n]["client"], robots[n]["mission"])) for n in active]
        for n, qid in queued:
            state = wait_done(robots[n]["client"], qid)
            if state != "Done":
                sys.exit(f"robot {n} cycle {cycle} ended {state}")
        levels = {n: battery(robots[n]["client"]) for n in robots}
        print(
            f"cycle {cycle}: doors delivered by {active} | battery "
            + " ".join(f"R{n}={levels[n]:.2f}%" for n in sorted(levels))
        )

        # Fleet-style rotation: weakest active robot swaps with the spare
        # once it drops below the threshold and the spare has more charge.
        weakest = min(active, key=lambda n: levels[n])
        if levels[weakest] < ROTATE_BELOW and levels[spare] > levels[weakest]:
            print(
                f"  rotating: R{weakest} ({levels[weakest]:.2f}%) -> charger, "
                f"R{spare} ({levels[spare]:.2f}%) -> line"
            )
            set_charging(robots[spare]["client"], False)  # off the charger, onto the line
            set_charging(robots[weakest]["client"], True)
            active[active.index(weakest)] = spare
            spare = weakest

    levels = {n: battery(robots[n]["client"]) for n in robots}
    print(
        f"\n{CYCLES} cycles complete. Final battery: "
        + " ".join(f"R{n}={levels[n]:.2f}%" for n in sorted(levels))
    )
    print("Real-world reference: ~3m50s per 130 m loop, one dryer off the line every 15 s.")


if __name__ == "__main__":
    main()
