#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""Visteon Tychy — on-demand cart requests from the floor.

Based on https://mobile-industrial-robots.com/cases/visteon
Four MiR200s at Visteon's cockpit-electronics plant (10,000 units/day,
24/5) run three jobs: hourly PCB deliveries to nine SMT lines, waste
collection from operators, and on-demand pickup of finished parts from
injection molding. Operators request a robot from a tablet button; ROEQ
click-in carts let the robot collect and release loads without hands.

What this exercises on the emulator:
  * mission authoring: POST /missions + POST /missions/{guid}/actions with
    a realistic cart action chain (docking, pickup_cart, move, place_cart,
    relative_move) — read back with GET /missions/{guid}/actions
  * a burst of on-demand requests draining FIFO through /mission_queue
  * DELETE /mission_queue/{id} — an operator cancels a request; the entry
    disappears from the queue (404 afterwards) while the rest keeps flowing

Run:
    uv run amr-emulator --mission-duration 2 &
    uv run scenarios/visteon_ondemand_carts.py
"""

import os
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"

REQUESTS = [
    ("SMT line 3", "PCB rack: warehouse -> SMT line 3"),
    ("line 5 operator", "Waste cart: collect from line 5 -> compactor"),
    ("injection molding 2", "Finished parts: IM press 2 -> assembly buffer"),
]

CART_ACTIONS = [
    ("docking", [{"id": "marker", "value": "cart_pickup_marker"}]),
    ("pickup_cart", []),
    ("move", [{"id": "position", "value": "dropoff"}]),
    ("place_cart", []),
    ("relative_move", [{"id": "x", "value": -0.5}]),
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
        sys.exit(f"{AMR_URL} does not look like the emulator; refusing to run a demo against it.")


def build_cart_mission(c: httpx.Client, group: str, name: str) -> str:
    guid = c.post(f"{API}/missions", json={"name": name, "group_id": group}).json()["guid"]
    for priority, (action_type, params) in enumerate(CART_ACTIONS, start=1):
        r = c.post(
            f"{API}/missions/{guid}/actions",
            json={
                "action_type": action_type,
                "mission_id": guid,
                "priority": priority,
                "parameters": params,
            },
        )
        r.raise_for_status()
    return guid


def main() -> None:
    c = client("visteon")
    require_emulator(c)
    c.put(f"{API}/status", json={"name": "MiR200-VIS-02"})

    group = c.get(f"{API}/mission_groups").json()[0]["guid"]
    missions = {}
    for requester, name in REQUESTS:
        guid = build_cart_mission(c, group, name)
        chain = [a["action_type"] for a in c.get(f"{API}/missions/{guid}/actions").json()]
        missions[requester] = guid
        print(f"mission ready for {requester}: {name}\n  action chain: {' -> '.join(chain)}")

    # The tablet buttons light up: three requests land at once.
    print("\nrequests come in:")
    queue = {}
    for requester, _ in REQUESTS:
        qid = c.post(f"{API}/mission_queue", json={"mission_id": missions[requester]}).json()["id"]
        queue[requester] = qid
        print(f"  [{qid}] {requester}")

    # The line 5 operator solved it themselves — cancel before it starts.
    cancel_who = "line 5 operator"
    c.delete(f"{API}/mission_queue/{queue[cancel_who]}").raise_for_status()
    print(f"\n{cancel_who} cancels their request -> [{queue[cancel_who]}]")

    remaining = {r: q for r, q in queue.items() if r != cancel_who}
    deadline = time.monotonic() + 90
    done = set()
    while len(done) < len(remaining) and time.monotonic() < deadline:
        for requester, qid in remaining.items():
            if requester in done:
                continue
            state = c.get(f"{API}/mission_queue/{qid}").json()["state"]
            if state == "Done":
                done.add(requester)
                print(f"  [{qid}] {requester}: Done")
        time.sleep(0.3)
    if len(done) < len(remaining):
        sys.exit("queue never drained")

    gone = c.get(f"{API}/mission_queue/{queue[cancel_who]}")
    if gone.status_code != 404:
        sys.exit(f"cancelled request should be gone (404), got {gone.status_code}: {gone.text}")
    live_ids = {e["id"] for e in c.get(f"{API}/mission_queue").json()}
    if queue[cancel_who] in live_ids:
        sys.exit("cancelled request still listed in the queue")
    print(f"\n  [{queue[cancel_who]}] {cancel_who}: removed from queue (GET now 404)")
    print("queue drained; cancelled request left no orphan entry")
    print("Real-world reference: 4 MiR200s, 10,000 cockpit units/day, ROI inside a year.")


if __name__ == "__main__":
    main()
