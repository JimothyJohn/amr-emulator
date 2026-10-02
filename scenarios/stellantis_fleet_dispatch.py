#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27"]
# ///
"""Stellantis Caen — fleet dispatch at production scale.

Based on https://mobile-industrial-robots.com/cases/stellantis-caen
43 robots (21 MiR1350 between lines and paint, 6 MiR1350 at cataphoresis,
16 MiR250 delivering boxes) complete ~1,000 missions per day, 24/7. A
supervision program validates each mission's prerequisites and lets MiR
Fleet allocate the best-placed robot.

What this exercises on the emulator (Fleet API, /api/v1):
  * x-api-key auth
  * GET /robots, GET /site/mission
  * POST /serial-order without robot-id — the fleet allocates round-robin
  * polling GET /serial-order/{id} until every phase completes
  * throughput extrapolation against the real plant's 1,000 missions/day

Run (fleet emulator, separate port so it can coexist with a robot emulator):
    uv run amr-emulator --fleet-version 1.5.0 --fleet-robots 3.8.1,3.8.1,3.8.1 \
        --port 9090 --mission-duration 2 &
    uv run scenarios/stellantis_fleet_dispatch.py
"""

import os
import sys
import time

import httpx

FLEET_URL = os.environ.get("AMR_FLEET_URL", "http://127.0.0.1:9090")
API = "/api/v1"
ORDERS = int(os.environ.get("ORDERS", "9"))


def client() -> httpx.Client:
    key = os.environ.get("AMR_FLEET_API_KEY", "distributor")
    return httpx.Client(base_url=FLEET_URL, headers={"x-api-key": key}, timeout=15)


def require_fleet(c: httpx.Client) -> None:
    try:
        index = c.get("/").json()
    except httpx.ConnectError:
        sys.exit(
            f"No fleet at {FLEET_URL} — start one:\n"
            "  uv run amr-emulator --fleet-version 1.5.0 "
            "--fleet-robots 3.8.1,3.8.1,3.8.1 --port 9090 --mission-duration 2"
        )
    if "fleet" not in str(index).lower():
        sys.exit(
            f"{FLEET_URL} does not look like the fleet emulator; refusing demo dispatch against it."
        )


def main() -> None:
    c = client()
    require_fleet(c)

    robots = c.get(f"{API}/robots").json()["robots"]
    print(f"fleet reports {len(robots)} robots:")
    for r in robots:
        print(f"  {r['name']} ({r['model']}, sw {r['software-version']}, {r['ip']})")

    missions = c.get(f"{API}/site/mission").json()["missions"]
    if not missions:
        sys.exit("fleet has no site missions to dispatch")
    mission_id = missions[0]["id"]
    print(
        f"\ndispatching {ORDERS} serial orders for mission {mission_id!r} (fleet picks the robot)"
    )

    t0 = time.monotonic()
    # serial-order id -> (robot allocated by the fleet, per-phase order ids)
    dispatched = {}
    for n in range(ORDERS):
        r = c.post(
            f"{API}/serial-order",
            json={"serial-order": {"priority": "Medium", "phases": [{"mission-id": mission_id}]}},
        )
        r.raise_for_status()
        sid = r.json()["id"]
        placed = c.get(f"{API}/serial-order/{sid}").json()
        dispatched[sid] = (placed["robot-id"], [p["order-id"] for p in placed["phases"]])
        print(f"  order {n + 1}/{ORDERS} accepted: {sid} -> robot {placed['robot-id'][-4:]}")

    print("\nwaiting for the fleet to work the backlog...")
    pending = {oid for _, order_ids in dispatched.values() for oid in order_ids}
    total = len(pending)
    deadline = time.monotonic() + 120
    per_robot: dict[str, int] = {}
    while pending and time.monotonic() < deadline:
        for oid in sorted(pending):
            order = c.get(f"{API}/order/{oid}").json()
            if order["order-status"] == "Finished":
                pending.discard(oid)
                robot = order["robot-name"]
                per_robot[robot] = per_robot.get(robot, 0) + 1
                print(f"  {oid} Finished on {robot} ({total - len(pending)}/{total})")
        time.sleep(0.5)
    if pending:
        sys.exit(f"orders never finished: {sorted(pending)}")

    elapsed = time.monotonic() - t0
    rate_per_day = ORDERS / elapsed * 86400
    print(f"\n{ORDERS} orders in {elapsed:.1f}s across robots {per_robot}")
    print(
        f"extrapolated: ~{rate_per_day:,.0f} missions/day at this cadence "
        "(the real Caen plant runs ~1,000/day on 43 robots)"
    )


if __name__ == "__main__":
    main()
