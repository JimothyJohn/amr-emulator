#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""DHL-style parcel hub — a warehouse control system over 12 AMRs.

Parcel carriers run MiR-class AMRs at DC scale behind a warehouse control
system (WCS) that owns dispatch, battery rotation, and incident recovery
(DHL describes the pattern in its logistics trend radar:
https://www.dhl.com/us-en/home/innovation-in-logistics/logistics-trend-radar/amr-logistics.html).
This script IS that WCS, pointed at 12 session-isolated emulated robots:

  * 120 transport orders in 3 arrival waves (dock -> staging -> outbound)
  * least-loaded dispatch with a 40% battery floor and shallow queues
  * charge rotation on /_emulator/battery (two robots start too low to work)
  * chaos mid-shift: an emergency stop on the busiest robot (jobs must be
    cancelled and re-dispatched; reset is physical, DELETE /_emulator/faults),
    then a mission_failure (aborted jobs re-dispatched after clear_error)
  * exit invariant: every order Done exactly once — the per-robot completion
    ledger must balance against the order book

What this exercises on the emulator:
  * X-AMR-Session at fleet scale (12 concurrent isolated robots; the cap is
    256 per process — past it the LRU session silently resets)
  * /_emulator/battery charge rotation, /_emulator/faults incident handling
  * sustained concurrent load (~50 req/s) with zero expected API errors

Run:
    uv run amr-emulator --mission-duration 2 &
    uv run scenarios/dhl_parcel_hub_wcs.py
"""

import asyncio
import os
import statistics
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"

N_ROBOTS = 12
N_ORDERS = 120
BATTERY_FLOOR = 40.0  # below this a robot gets no freight
CHARGE_TARGET = 85.0
MAX_QUEUE = 3  # shallow queues keep re-dispatch cheap
STALL_S = 15.0  # job stuck in one state this long -> robot is down
DEADLINE_S = 240.0

ROUTES = ["Inbound dock -> Staging", "Staging -> Outbound lane", "Empty cart return"]
START_BATTERY = [82, 74, 91, 66, 88, 35, 79, 93, 71, 28, 85, 77]  # R06, R10 start low

api_calls = 0
api_errors = 0
latencies_ms: list[float] = []


class Robot:
    def __init__(self, idx: int, client: httpx.AsyncClient):
        self.name = f"DC-R{idx + 1:02d}"
        self.c = client
        self.mission_guids: dict[str, str] = {}
        self.charging = False
        self.down = False  # quarantined by the WCS
        self.jobs: dict[int, Order] = {}  # open queue id -> order
        self.completed = 0

    async def req(self, method: str, path: str, **kw):
        global api_calls, api_errors
        t0 = time.perf_counter()
        r = await self.c.request(method, path, **kw)
        latencies_ms.append((time.perf_counter() - t0) * 1000)
        api_calls += 1
        if r.status_code >= 400:
            api_errors += 1
            print(f"  !! API {r.status_code} {method} {path}: {r.text[:100]}")
        return r


class Order:
    def __init__(self, oid: int, route: str, wave: int):
        self.oid = oid
        self.route = route
        self.wave = wave
        self.state = "PENDING"  # PENDING -> DISPATCHED -> DONE
        self.robot: Robot | None = None
        self.job_id: int | None = None
        self.attempts = 0
        self.dispatched_at = 0.0
        self.done_at = 0.0
        self.job_state_since = 0.0
        self.last_job_state = ""


def require_emulator() -> None:
    try:
        index = httpx.get(AMR_URL + "/", timeout=5).json()
    except httpx.ConnectError:
        sys.exit(f"Nothing at {AMR_URL} — start one: uv run amr-emulator --mission-duration 2")
    if "emulated_mir_version" not in index:
        sys.exit(f"{AMR_URL} does not look like the emulator; refusing to inject faults into it.")


async def bring_up(robots: list["Robot"]):
    async def one(i: int, r: Robot):
        await r.req(
            "PUT",
            f"{API}/status",
            json={"name": r.name, "position": {"x": 5.0 + 2.5 * i, "y": 5.0, "orientation": 0}},
        )
        await r.req("PUT", "/_emulator/battery", json={"percentage": START_BATTERY[i]})
        group = (await r.req("GET", f"{API}/mission_groups")).json()[0]["guid"]
        for route in ROUTES:
            resp = await r.req("POST", f"{API}/missions", json={"name": route, "group_id": group})
            r.mission_guids[route] = resp.json()["guid"]

    await asyncio.gather(*(one(i, r) for i, r in enumerate(robots)))


async def dispatch(order: Order, robot: Robot):
    order.attempts += 1
    resp = await robot.req(
        "POST", f"{API}/mission_queue", json={"mission_id": robot.mission_guids[order.route]}
    )
    entry = resp.json()
    order.state, order.robot, order.job_id = "DISPATCHED", robot, entry["id"]
    order.dispatched_at = order.dispatched_at or time.monotonic()
    order.last_job_state, order.job_state_since = entry["state"], time.monotonic()
    robot.jobs[entry["id"]] = order


async def quarantine(robot: Robot, reason: str, orders_back: list[Order]):
    """Pull a robot from rotation: cancel its queue, return orders to PENDING."""
    robot.down = True
    await robot.req("DELETE", f"{API}/mission_queue")
    for order in robot.jobs.values():
        order.state, order.robot, order.job_id = "PENDING", None, None
        orders_back.append(order)
    n = len(robot.jobs)
    robot.jobs.clear()
    print(f"  ** {robot.name} quarantined ({reason}); {n} job(s) returned to the order pool")


async def main():
    require_emulator()
    token = robot_token(
        os.environ.get("AMR_USERNAME", "distributor"),
        os.environ.get("AMR_PASSWORD", "distributor"),
    )
    limits = httpx.Limits(max_connections=64)
    clients = [
        httpx.AsyncClient(
            base_url=AMR_URL,
            headers={"Authorization": f"Basic {token}", "X-AMR-Session": f"dhl-DC-R{i + 1:02d}"},
            timeout=10.0,
            limits=limits,
        )
        for i in range(N_ROBOTS)
    ]
    robots = [Robot(i, c) for i, c in enumerate(clients)]

    print(f"=== BRING-UP: {N_ROBOTS} robots, mission library, seeded batteries ===")
    t_start = time.monotonic()
    await bring_up(robots)
    low = [
        f"{r.name}({START_BATTERY[i]}%)"
        for i, r in enumerate(robots)
        if START_BATTERY[i] < BATTERY_FLOOR
    ]
    print(f"  up in {time.monotonic() - t_start:.2f}s; below the floor: {', '.join(low)}")

    orders = [
        Order(i + 1, ROUTES[i % len(ROUTES)], wave=(0 if i < 50 else 1 if i < 90 else 2))
        for i in range(N_ORDERS)
    ]
    waves_released = 1
    estop_fired = failure_fired = False
    estop_robot: Robot | None = None
    estop_at = 0.0
    charge_events = redispatches = 0

    print(f"=== SHIFT START: {N_ORDERS} orders in 3 waves ===")
    last_report = 0.0
    while True:
        now = time.monotonic()
        if now - t_start > DEADLINE_S:
            sys.exit(f"BUG: shift did not finish inside {DEADLINE_S}s")

        done = sum(1 for o in orders if o.state == "DONE")
        if done == N_ORDERS:
            break
        if waves_released == 1 and done >= 35:
            waves_released = 2
            print("  -- wave 2 released")
        if waves_released == 2 and done >= 75:
            waves_released = 3
            print("  -- wave 3 released")

        # ---- refresh: status + queue for every robot, in parallel ----------
        statuses = await asyncio.gather(*(r.req("GET", f"{API}/status") for r in robots))
        queues = await asyncio.gather(*(r.req("GET", f"{API}/mission_queue") for r in robots))
        state = {r.name: s.json() for r, s in zip(robots, statuses, strict=True)}
        queue_map = {
            r.name: {e["id"]: e for e in q.json()} for r, q in zip(robots, queues, strict=True)
        }

        # ---- reconcile job states: completions, aborts, stalls -------------
        returned: list[Order] = []
        for r in robots:
            for jid, order in list(r.jobs.items()):
                entry = queue_map[r.name].get(jid)
                jstate = entry["state"] if entry else "GONE"
                if jstate != order.last_job_state:
                    order.last_job_state, order.job_state_since = jstate, now
                if jstate == "Done":
                    order.state, order.done_at = "DONE", now
                    r.completed += 1
                    del r.jobs[jid]
                elif jstate in ("Aborted", "GONE"):
                    order.state, order.robot, order.job_id = "PENDING", None, None
                    returned.append(order)
                    del r.jobs[jid]
                    redispatches += 1
                elif now - order.job_state_since > STALL_S and not r.down:
                    await quarantine(r, f"job {jid} stalled in {jstate}", returned)
                    break

        # ---- robot health, straight from /status ---------------------------
        for r in robots:
            s = state[r.name]
            if r.down:
                continue
            if s["state_text"] == "EmergencyStop":
                await quarantine(r, "emergency stop reported", returned)
            elif s["state_text"] == "Error":
                await r.req("PUT", f"{API}/status", json={"clear_error": True})
                print(f"  ** {r.name} Error state: clear_error sent")

        # ---- battery rotation ------------------------------------------------
        for r in robots:
            if r.down:
                continue
            batt = state[r.name]["battery_percentage"]
            if not r.charging and batt < BATTERY_FLOOR and not r.jobs:
                await r.req(
                    "PUT",
                    "/_emulator/battery",
                    json={"charging": True, "charge_rate": 6, "target": CHARGE_TARGET},
                )
                r.charging = True
                charge_events += 1
                print(f"  -- {r.name} at {batt:.1f}%: off to the charger")
            elif r.charging and batt >= CHARGE_TARGET:
                await r.req("PUT", "/_emulator/battery", json={"charging": False})
                r.charging = False
                print(f"  -- {r.name} charged to {batt:.1f}%: back in rotation")

        # ---- chaos, scripted -------------------------------------------------
        if not estop_fired and done >= 30:
            estop_fired = True
            busiest = max((r for r in robots if not r.down), key=lambda r: (len(r.jobs), r.name))
            await busiest.req("PUT", "/_emulator/faults", json={"faults": ["emergency_stop"]})
            estop_robot, estop_at = busiest, now
            print(f"  !! CHAOS: emergency stop pressed on {busiest.name}")
        if estop_robot and estop_robot.down and now - estop_at > 8.0:
            await estop_robot.req("DELETE", "/_emulator/faults")
            s = (await estop_robot.req("GET", f"{API}/status")).json()
            if s["state_text"] == "Ready":
                estop_robot.down = False
                print(f"  !! {estop_robot.name}: physical reset, health probe Ready, rejoining")
                estop_robot = None
        if not failure_fired and done >= 60:
            failure_fired = True
            victim = max(
                (r for r in robots if not r.down and r.jobs), key=lambda r: (len(r.jobs), r.name)
            )
            await victim.req("PUT", "/_emulator/faults", json={"faults": ["mission_failure"]})
            print(f"  !! CHAOS: mission controller failure on {victim.name}")

        # ---- dispatch: least-loaded eligible robot ---------------------------
        pending = [o for o in orders if o.state == "PENDING" and o.wave < waves_released]
        eligible = [
            r
            for r in robots
            if not r.down
            and not r.charging
            and state[r.name]["battery_percentage"] >= BATTERY_FLOOR
        ]
        assignments = []
        for order in pending:
            open_slots = [r for r in eligible if len(r.jobs) < MAX_QUEUE]
            if not open_slots:
                break
            target = min(open_slots, key=lambda r: (len(r.jobs), r.name))
            assignments.append((order, target))
            target.jobs[-order.oid] = order  # placeholder so load balancing sees it
        for order, target in assignments:
            del target.jobs[-order.oid]
        await asyncio.gather(*(dispatch(o, t) for o, t in assignments))

        if now - last_report > 5.0:
            last_report = now
            active = sum(len(r.jobs) for r in robots)
            charging = [r.name for r in robots if r.charging]
            downs = [r.name for r in robots if r.down]
            print(
                f"  t+{now - t_start:5.1f}s  done {done:3d}/{N_ORDERS}  in-flight {active:2d}  "
                f"charging {charging or '-'}  down {downs or '-'}"
            )
        await asyncio.sleep(0.5)

    wall = time.monotonic() - t_start
    print(f"\n=== SHIFT COMPLETE in {wall:.1f}s wall ===")

    if not all(o.state == "DONE" for o in orders):
        sys.exit("BUG: lost orders")
    if sum(r.completed for r in robots) != N_ORDERS:
        sys.exit("BUG: completion ledger does not balance against the order book")
    cycle = [o.done_at - o.dispatched_at for o in orders]
    retried = [o for o in orders if o.attempts > 1]
    print(f"  orders: {N_ORDERS}/{N_ORDERS} Done, exactly once (ledger balances)")
    print(
        f"  cycle time: p50 {statistics.median(cycle):.1f}s  "
        f"p95 {statistics.quantiles(cycle, n=20)[18]:.1f}s  max {max(cycle):.1f}s"
    )
    print(
        f"  re-dispatched after incidents: {len(retried)} orders; charge rotations: {charge_events}"
    )
    print("  per-robot completions: " + ", ".join(f"{r.name[-3:]}:{r.completed}" for r in robots))

    lat = sorted(latencies_ms)
    print(f"\n  emulator: {api_calls} calls, {api_errors} errors, {api_calls / wall:.0f} req/s")
    print(
        f"  latency p50 {lat[len(lat) // 2]:.1f}ms  "
        f"p95 {lat[int(len(lat) * 0.95)]:.1f}ms  max {lat[-1]:.1f}ms"
    )
    if api_errors:
        sys.exit("BUG: the emulator returned errors under load")

    for c in clients:
        await c.aclose()


if __name__ == "__main__":
    asyncio.run(main())
