#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""Machine shop — one robot feeds five bar-fed lathes from a central rod rack.

The classic 1-to-many machine-tending pattern (no MiR-official case study;
composite of published bar-feeder replenishment deployments). A machine shop
runs five CNC lathes, each with a bar feeder holding a short magazine of
cylindrical rods. The feeders chew through stock at different rates — part
cycle times differ per lathe — and a single MiR shuttles rod bundles from the
central storage rack to whichever feeder is running lowest. The whole tension
of a 1-to-many cell is here: one robot, five consumers, and a day clock that
never stops for the robot.

What this exercises on the emulator:
  * GET/PUT /registers/{n} as machine-side telemetry: each bar feeder
    publishes its magazine level, the rack publishes remaining stock
  * lowest-stock-first dispatch — the priority decision lives in the shop's
    dispatcher, not the robot's FIFO queue (which only ever holds one job)
  * per-lathe X-AMR-Mission-Duration in *simulated* seconds — near lathes
    are a 1-minute (~30 m) run, the far wall 3 minutes (~90 m)
  * PUT /_emulator/clock at 60x: those realistic trips finish in 1-3 wall
    seconds while odometry, /statistics/distance, battery drain, and
    timestamps all come out shift-realistic. The clock is process-wide
    (every session on the emulator), so the script restores it on exit —
    but anything else running against the same process meanwhile will see
    time fly.
  * a rod-conservation ledger: rack out == magazines in, checked exactly at
    end of day, plus a zero-starvation assertion (no lathe ever waits on air)

Register map used here (pick your own on a real site):
  30-34  bar feeder magazine level, lathes L1-L5 (rods remaining)
  50     central rack stock (rods remaining)

Run:
    uv run amr-emulator --mission-duration 2 &
    uv run scenarios/machineshop_barfeed_lathes.py
"""

import os
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"

# The compressed production day: consumption advances once per tick whether
# or not the robot is moving. The emulator clock runs at TIME_SCALE, so
# trip durations below are simulated seconds (wall = sim / TIME_SCALE) and
# odometry comes out realistic (the emulator drives 0.5 m per sim second).
DAY_TICKS = 120
TICK_S = 0.25
TIME_SCALE = 60

MAGAZINE_CAP = 8  # rods a bar feeder holds
REORDER_AT = 3  # dispatch a refill at or below this level
RACK_INITIAL = 80  # rods on the central storage rack at shift start
RACK_REG = 50

# One row per lathe: PLC register for its magazine, delivery duration from
# the rack (X-AMR-Mission-Duration, emulator-only, in simulated seconds —
# near bays are a 1-minute / ~30 m run, the far wall 3 minutes / ~90 m),
# and part cycle time as ticks-per-rod.
LATHES = [
    {"name": "L1 (near bay)", "reg": 30, "trip_s": "60", "ticks_per_rod": 8},
    {"name": "L2 (near bay)", "reg": 31, "trip_s": "60", "ticks_per_rod": 10},
    {"name": "L3 (mid aisle)", "reg": 32, "trip_s": "120", "ticks_per_rod": 12},
    {"name": "L4 (mid aisle)", "reg": 33, "trip_s": "120", "ticks_per_rod": 14},
    {"name": "L5 (far wall)", "reg": 34, "trip_s": "180", "ticks_per_rod": 16},
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
        sys.exit(f"Nothing at {AMR_URL} — start one: uv run amr-emulator --mission-duration 2")
    if "emulated_mir_version" not in index:
        sys.exit(
            f"{AMR_URL} does not look like the emulator; refusing to write PLC registers on it."
        )


def reg_get(c: httpx.Client, n: int) -> int:
    return int(c.get(f"{API}/registers/{n}").json()["value"])


def reg_set(c: httpx.Client, n: int, value: int) -> None:
    c.put(f"{API}/registers/{n}", json={"value": value}).raise_for_status()


def queue_state(c: httpx.Client, qid: int) -> str:
    return c.get(f"{API}/mission_queue/{qid}").json()["state"]


def main() -> None:
    c = client("machineshop")
    require_emulator(c)
    # 60x simulated time makes the realistic trip durations fit the wall
    # clock. Process-wide, so restore it however the shift ends.
    c.put("/_emulator/clock", json={"scale": TIME_SCALE}).raise_for_status()
    try:
        run_shift(c)
    finally:
        c.delete("/_emulator/clock")


def run_shift(c: httpx.Client) -> None:
    c.put(f"{API}/status", json={"name": "BarRunner"})
    start = c.get(f"{API}/status").json()

    group = c.get(f"{API}/mission_groups").json()[0]["guid"]
    for lathe in LATHES:
        lathe["mission"] = c.post(
            f"{API}/missions",
            json={"name": f"Bar stock: rack -> {lathe['name']}", "group_id": group},
        ).json()["guid"]
        lathe["level"] = MAGAZINE_CAP
        lathe["consumed"] = 0
        lathe["deliveries"] = 0
        lathe["min_level"] = MAGAZINE_CAP
        lathe["starved"] = 0
        reg_set(c, lathe["reg"], MAGAZINE_CAP)
    rack = RACK_INITIAL
    reg_set(c, RACK_REG, rack)
    print(
        f"shift start: {len(LATHES)} lathes at {MAGAZINE_CAP} rods each, "
        f"rack at {rack}, reorder point {REORDER_AT}\n"
    )

    in_flight = None  # {"qid", "lathe", "bundle"} while the robot is out
    busy_ticks = 0

    def land(delivery: dict) -> None:
        lathe = delivery["lathe"]
        lathe["level"] += delivery["bundle"]
        lathe["deliveries"] += 1
        reg_set(c, lathe["reg"], lathe["level"])
        print(
            f"  tick {tick:3d}: +{delivery['bundle']} rods to {lathe['name']} "
            f"(magazine {lathe['level']}, rack {rack})"
        )

    for tick in range(1, DAY_TICKS + 1):
        time.sleep(TICK_S)

        # Bar feeders consume on their own clocks; a dry feeder is a stopped
        # spindle, not a consumed rod.
        for lathe in LATHES:
            if tick % lathe["ticks_per_rod"] == 0:
                if lathe["level"] > 0:
                    lathe["level"] -= 1
                    lathe["consumed"] += 1
                    reg_set(c, lathe["reg"], lathe["level"])
                else:
                    lathe["starved"] += 1
                lathe["min_level"] = min(lathe["min_level"], lathe["level"])

        if in_flight is not None:
            busy_ticks += 1
            if queue_state(c, in_flight["qid"]) == "Done":
                land(in_flight)
                in_flight = None

        if in_flight is None:
            # The 1-to-many decision: of everyone at or below the reorder
            # point (per their registers), serve the lowest magazine first.
            low = [x for x in LATHES if reg_get(c, x["reg"]) <= REORDER_AT]
            if low:
                lathe = min(low, key=lambda x: x["level"])
                bundle = min(MAGAZINE_CAP - lathe["level"], rack)
                if bundle <= 0:
                    sys.exit(f"rack empty at tick {tick} — shift under-stocked")
                rack -= bundle
                reg_set(c, RACK_REG, rack)
                qid = c.post(
                    f"{API}/mission_queue",
                    json={"mission_id": lathe["mission"]},
                    headers={"X-AMR-Mission-Duration": lathe["trip_s"]},
                ).json()["id"]
                in_flight = {"qid": qid, "lathe": lathe, "bundle": bundle}
                trip_sim = int(lathe["trip_s"])
                print(
                    f"  tick {tick:3d}: {lathe['name']} at {lathe['level']} rods -> "
                    f"picked {bundle} from rack, queued [{qid}] "
                    f"({trip_sim // 60} min / ~{trip_sim * 0.5:.0f} m run)"
                )

    # A bundle picked before the whistle still gets delivered.
    if in_flight is not None:
        deadline = time.monotonic() + 60
        while queue_state(c, in_flight["qid"]) != "Done":
            if time.monotonic() > deadline:
                sys.exit(f"final delivery [{in_flight['qid']}] never finished")
            time.sleep(0.2)
        tick = DAY_TICKS
        land(in_flight)

    print("\nend of shift:")
    consumed_total = 0
    for lathe in LATHES:
        consumed_total += lathe["consumed"]
        spindle_pct = 100 * (1 - lathe["starved"] * lathe["ticks_per_rod"] / DAY_TICKS)
        print(
            f"  {lathe['name']:14s} consumed {lathe['consumed']:2d} rods over "
            f"{lathe['deliveries']} deliveries, min magazine {lathe['min_level']}, "
            f"spindle uptime {spindle_pct:.0f}%"
        )
    print(
        f"  BarRunner busy {100 * busy_ticks / DAY_TICKS:.0f}% of the day; "
        f"rack {RACK_INITIAL} -> {rack}"
    )
    end = c.get(f"{API}/status").json()
    print(
        f"  odometer +{end['moved'] - start['moved']:.0f} m for the day; "
        f"battery {start['battery_percentage']:.0f}% -> {end['battery_percentage']:.1f}%"
    )

    # Conservation of rods: every rod is on the rack, in a magazine, or
    # already turned into parts. Registers must agree with the ledger.
    magazines = sum(x["level"] for x in LATHES)
    if RACK_INITIAL + len(LATHES) * MAGAZINE_CAP != rack + magazines + consumed_total:
        sys.exit(
            f"rod ledger broken: rack {rack} + magazines {magazines} "
            f"+ consumed {consumed_total} != {RACK_INITIAL + len(LATHES) * MAGAZINE_CAP}"
        )
    rack_reg = reg_get(c, RACK_REG)
    if rack_reg != rack:
        sys.exit(f"rack register {rack_reg} != ledger {rack}")
    for lathe in LATHES:
        level_reg = reg_get(c, lathe["reg"])
        if level_reg != lathe["level"]:
            sys.exit(f"{lathe['name']} register {level_reg} != ledger {lathe['level']}")
    starved_total = sum(x["starved"] for x in LATHES)
    if starved_total:
        sys.exit(f"{starved_total} starvation events — one robot did not keep up")
    print("\nrod ledger balances exactly; zero starvation events — one robot fed five lathes")


if __name__ == "__main__":
    main()
