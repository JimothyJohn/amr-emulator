"""Drive the InOrbit/OTTO vda5050_connector (running in Docker with a mock
robot adapter) using the vda5050-emulator's MasterControl over the emulator's
embedded broker. Master-side external validation: their robot stack, our
master + broker."""

import asyncio
import time

from vda5050_emulator import MasterControl, make_action, make_edge, make_node

T0 = time.monotonic()


def log(side: str, text: str) -> None:
    print(f"t+{time.monotonic() - T0:6.2f}s [{side:9s}] {text}", flush=True)


async def main() -> None:
    log("broker", "reusing the vda5050-emulator's embedded broker already on :1884")
    master = MasterControl(
        "127.0.0.1",
        1884,
        manufacturer="robots",
        serial_number="robot_1",
        version="2.0.0",
    )
    await master.connect()
    log("master", "MasterControl connected, waiting for the connector to appear")

    state = await master.next_state(timeout=120)
    log(
        "robot>us",
        f"first state: operatingMode={state.get('operatingMode')} "
        f"battery={state.get('batteryState', {}).get('batteryCharge')}%",
    )
    while not master.connections:
        await asyncio.sleep(0.2)
    log("robot>us", f"connection: {master.connections[-1]['connectionState']}")

    beep = make_action("detectObject", blocking_type="NONE")
    nodes = [
        make_node("wp0", 0, x=0.0, y=0.0, theta=0.0),
        make_node("wp1", 2, x=1.5, y=0.0, theta=0.0),
        make_node("wp2", 4, x=1.5, y=1.5, theta=0.0, actions=[beep]),
    ]
    # The connector's deserializer requires theta (optional per spec) and
    # 2.x-float deviations; give the first node a generous float deviation.
    nodes[0]["nodePosition"]["allowedDeviationXY"] = 10.0
    edges = [
        make_edge("e0", 1, start_node_id="wp0", end_node_id="wp1", version="2.0.0"),
        make_edge("e1", 3, start_node_id="wp1", end_node_id="wp2", version="2.0.0"),
    ]
    await master.send_order(nodes, edges, order_id="order-inorbit-1")
    log("us>robot", "order order-inorbit-1: 3 nodes, 2 edges, 1 attached action")

    last = ""
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            state = await master.next_state(
                lambda s: (
                    f"{s.get('lastNodeId')}|{len(s.get('nodeStates', []))}"
                    f"|{[a.get('actionStatus') for a in s.get('actionStates', [])]}"
                )
                != last,
                timeout=30,
                past=False,
            )
        except TimeoutError:
            break
        last = (
            f"{state.get('lastNodeId')}|{len(state.get('nodeStates', []))}"
            f"|{[a.get('actionStatus') for a in s.get('actionStates', [])] if (s := state) else []}"
        )
        log(
            "robot>us",
            f"state: lastNodeId={state.get('lastNodeId')!r} "
            f"seq={state.get('lastNodeSequenceId')} "
            f"nodeStates={len(state.get('nodeStates', []))} "
            f"actions={[(a.get('actionType'), a.get('actionStatus')) for a in state.get('actionStates', [])]} "
            f"errors={[e.get('errorType') for e in state.get('errors', [])]}",
        )
        if state.get("lastNodeId") == "wp2" and not state.get("nodeStates"):
            actions = state.get("actionStates", [])
            if all(a.get("actionStatus") in ("FINISHED", "FAILED") for a in actions):
                log("result", "order complete: robot at wp2, all action states terminal")
                print("\nRESULT: order COMPLETED by InOrbit vda5050_connector", flush=True)
                break
    else:
        print("\nRESULT: TIMEOUT", flush=True)

    await master.disconnect()


asyncio.run(main())
