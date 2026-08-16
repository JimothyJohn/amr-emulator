"""Drive one mission from Isaac Mission Dispatch through the vda5050-emulator
and print a timestamped transcript of both sides."""

import json
import queue
import threading
import time
import urllib.request

import paho.mqtt.client as paho

API = "http://127.0.0.1:5050"
PREFIX = "uagv/v2/RobotCompany/carter01"
T0 = time.monotonic()


def stamp() -> str:
    return f"t+{time.monotonic() - T0:6.2f}s"


def log(side: str, text: str) -> None:
    print(f"{stamp()} [{side:7s}] {text}", flush=True)


def api(path: str, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def watch_mqtt(inbox: queue.Queue) -> paho.Client:
    client = paho.Client(
        callback_api_version=paho.CallbackAPIVersion.VERSION2,
        client_id="validator",
        protocol=paho.MQTTv311,
    )
    client.on_message = lambda _c, _u, m: inbox.put(m)
    client.connect("127.0.0.1", 1884)
    client.subscribe(f"{PREFIX}/order")
    client.subscribe(f"{PREFIX}/instantActions")
    client.subscribe(f"{PREFIX}/state")
    client.loop_start()
    return client


def mqtt_logger(inbox: queue.Queue, stop: threading.Event) -> None:
    last_state_line = ""
    while not stop.is_set():
        try:
            m = inbox.get(timeout=0.3)
        except queue.Empty:
            continue
        doc = json.loads(m.payload)
        name = m.topic.rsplit("/", 1)[1]
        if name == "order":
            nodes = [n["nodeId"] for n in doc["nodes"]]
            log(
                "MD>robot",
                f"order {doc['orderId']} (update {doc['orderUpdateId']}): "
                f"{len(doc['nodes'])} nodes {nodes}",
            )
        elif name == "instantActions":
            array = doc.get("actions") or doc.get("instantActions") or []
            kinds = [a.get("actionType") for a in array]
            field = "actions" if "actions" in doc else "instantActions (1.x-style field)"
            log("MD>robot", f"instantActions via {field}: {kinds}")
        elif name == "state":
            pos = doc.get("agvPosition", {})
            line = (
                f"state: lastNodeId={doc['lastNodeId']!r} seq={doc['lastNodeSequenceId']} "
                f"driving={doc['driving']} pos=({pos.get('x', 0):.2f},{pos.get('y', 0):.2f}) "
                f"battery={doc['batteryState']['batteryCharge']:.1f}% "
                f"errors={[e['errorType'] for e in doc['errors']]}"
            )
            if line != last_state_line:
                log("robot>MD", line)
                last_state_line = line


def main() -> None:
    inbox: queue.Queue = queue.Queue()
    stop = threading.Event()
    client = watch_mqtt(inbox)
    logger = threading.Thread(target=mqtt_logger, args=(inbox, stop), daemon=True)
    logger.start()

    robot = api("/robot")[0]
    log("MD api", f"robot carter01 online={robot['status']['online']} "
                  f"battery={robot['status']['battery_level']:.1f}% "
                  f"pose=({robot['status']['pose']['x']:.2f},{robot['status']['pose']['y']:.2f})")

    mission = {
        "robot": "carter01",
        "mission_tree": [
            {
                "name": "goto_pickup",
                "parent": "root",
                "route": {
                    "waypoints": [
                        {"x": 2.0, "y": 0.0, "theta": 0, "map_id": ""},
                        {"x": 2.0, "y": 2.0, "theta": 1.57, "map_id": ""},
                    ]
                },
            },
            {
                "name": "goto_dropoff",
                "parent": "root",
                "route": {
                    "waypoints": [
                        {"x": 0.0, "y": 2.0, "theta": 3.14, "map_id": ""},
                    ]
                },
            },
        ],
    }
    created = api("/mission", mission)
    name = created["name"]
    log("MD api", f"mission {name} submitted (2 route nodes, 3 waypoints total)")

    seen_states = set()
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        status = next(m for m in api("/mission") if m["name"] == name)["status"]
        key = (status["state"], json.dumps(status["node_status"], sort_keys=True))
        if key not in seen_states:
            seen_states.add(key)
            nodes = {
                k: v["state"]
                for k, v in status["node_status"].items()
                if k != "root"
            }
            log("MD api", f"mission {status['state']} nodes={nodes}")
        if status["state"] in ("COMPLETED", "FAILED"):
            break
        time.sleep(1)

    robot = api("/robot")[0]
    log("MD api", f"final robot pose=({robot['status']['pose']['x']:.2f},"
                  f"{robot['status']['pose']['y']:.2f}) state={robot['status']['state']}")
    stop.set()
    client.loop_stop()
    client.disconnect()
    final = next(m for m in api("/mission") if m["name"] == name)["status"]["state"]
    print(f"\nRESULT: mission {final}", flush=True)


if __name__ == "__main__":
    main()
