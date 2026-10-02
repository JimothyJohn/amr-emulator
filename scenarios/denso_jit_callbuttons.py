#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "amr-client"]
#
# [tool.uv.sources]
# amr-client = { path = "../packages/amr-client" }
# ///
"""DENSO — just-in-time delivery from PLC call buttons and door I/O.

Based on https://mobile-industrial-robots.com/cases/denso
Six MiR250s (plus five MiR500s on order) killed the 12-miles-a-day walk at
DENSO's US plants: associates request material from floor-level buttons,
missions integrate over the REST API, and wireless I/O modules open doors
for cleanroom access. 500,000+ missions since 2020, ROI inside a year.

What this exercises on the emulator:
  * GET/PUT /registers/{n} — the robot's PLC register bank as the
    integration surface: call buttons in, door control out
  * a dispatcher loop: poll buttons -> enqueue the right mission ->
    drive door state while the mission executes

Register map used here (pick your own on a real site):
  10  call button, assembly line A     (operator writes 1, dispatcher clears)
  11  call button, assembly line B
  20  cleanroom door command           (1 = open, 0 = closed)

Run:
    uv run amr-emulator --mission-duration 2 &
    uv run scenarios/denso_jit_callbuttons.py
"""

import os
import sys
import time

import httpx
from amr_client import robot_token

AMR_URL = os.environ.get("AMR_URL", "http://127.0.0.1:8080")
API = "/api/v2.0.0"
BUTTONS = {10: "assembly line A", 11: "assembly line B"}
DOOR = 20


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


def wait_done(c: httpx.Client, qid: int, timeout: float = 60.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if c.get(f"{API}/mission_queue/{qid}").json()["state"] == "Done":
            return
        time.sleep(0.2)
    raise TimeoutError(f"queue {qid} not done")


def main() -> None:
    c = client("denso")
    require_emulator(c)

    group = c.get(f"{API}/mission_groups").json()[0]["guid"]
    missions = {}
    for reg, line in BUTTONS.items():
        name = f"JIT: warehouse -> {line} (through cleanroom door)"
        missions[reg] = c.post(f"{API}/missions", json={"name": name, "group_id": group}).json()[
            "guid"
        ]
    for reg in (*BUTTONS, DOOR):
        reg_set(c, reg, 0)
    print(f"register map armed: buttons {sorted(BUTTONS)}, door {DOOR}; missions created\n")

    # Associates on the floor press their buttons (writes any WMS/PLC could make).
    for reg, line in BUTTONS.items():
        reg_set(c, reg, 1)
        print(f"operator at {line} presses call button (register {reg} <- 1)")

    # Dispatcher: poll buttons, clear them, enqueue, run the door while executing.
    print("\ndispatcher loop:")
    for reg, line in BUTTONS.items():
        if reg_get(c, reg) != 1:
            continue
        reg_set(c, reg, 0)
        qid = c.post(f"{API}/mission_queue", json={"mission_id": missions[reg]}).json()["id"]
        print(f"  button {reg} ({line}): cleared, mission queued as [{qid}]")

        # open the door as soon as the robot is moving, close it when done
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if c.get(f"{API}/mission_queue/{qid}").json()["state"] == "Executing":
                break
            time.sleep(0.2)
        reg_set(c, DOOR, 1)
        print(
            f"    robot en route -> door register {DOOR} <- 1 (open), readback={reg_get(c, DOOR)}"
        )
        wait_done(c, qid)
        reg_set(c, DOOR, 0)
        print(f"    delivery to {line} Done -> door closed, readback={reg_get(c, DOOR)}")

    leftover = {n: reg_get(c, n) for n in (*BUTTONS, DOOR)}
    if any(leftover.values()):
        sys.exit(f"registers not cleaned up: {leftover}")
    print(f"\nboth lines served just-in-time; registers back to idle {leftover}")
    print("Real-world reference: DENSO runs this pattern 24/7 — 500,000+ missions since 2020.")


if __name__ == "__main__":
    main()
