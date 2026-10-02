# amr-client

Typed Python client for the **MiR robot REST API** (`amr_client.robot`) and the
**MiR Fleet Enterprise Integration API** (`amr_client.fleet`), generated from
the official specs bundled with [amr-emulator](https://github.com/JimothyJohn/amr-emulator).

`amr_client/robot`, `amr_client/fleet`, and `_provenance.py` are entirely
generated (`scripts/generate_client.py`); CI fails if they drift from the spec
registry. Never hand-edit them.

```python
from amr_client import robot_client, fleet_client
from amr_client.robot.api.default import get_status

client = robot_client("http://192.168.12.20")  # or the emulator
status = get_status.sync(client=client)
print(status.state_text, status.battery_percentage)
```

## Find robots on the network — `scan_network()` / `amr-discover`

Don't know the robot's IP? Sweep the network for it:

```console
$ amr-discover                     # scan the local /24 on ports 80, 8080
Found 1 MiR target(s):
  http://192.168.12.20  [robot] 3.8.1

$ amr-discover 192.168.12.0/24     # a specific subnet
$ amr-discover mir.local:8080      # a specific host[:port]
$ amr-discover --json              # machine-readable
```

```python
from amr_client import scan_network, connect

for target in scan_network():  # local /24, ports 80 + 8080
    print(target.url, target.info.kind, target.info.version)

first = scan_network(["192.168.12.0/24"])[0]  # or a CIDR / host list
client = connect(first.url)  # drive the one it found
```

Each candidate gets a cheap TCP connect, then the identification handshake
below — only confirmed MiR robots/fleets/dispatchers come back, and every
step runs under a hard deadline so a hung or noisy host can't stall the
sweep. All probes are unauthenticated reads. `scan_network_async()` is the
async twin.

## Version discovery — `connect()`

You don't have to know (or install) the version the target runs. `connect()`
performs a connect-time handshake — it asks the target what it is and which
MiR software version it reports — and returns the right client:

```python
from amr_client import connect, detect_server

client = connect("http://127.0.0.1:8080")  # robot, fleet, or the
client = connect("https://demo.example.com")  # multi-version dispatcher
client = connect("https://demo.example.com", version="2.14.7")  # pin a mount

info = detect_server("http://127.0.0.1:8080")  # just ask, don't build
print(info.kind, info.version)  # e.g. "robot 3.8.1"
```

The handshake probes, in order: `/healthz` (dispatcher manifest), `/` (the
emulator's JSON index), `/api/v1/system/version` (official Fleet endpoint,
works on real fleets), `/swagger.json` (`info.version`), then a bare
`/api/v2.0.0/status` (proves a robot; version stays unknown). All probes are
unauthenticated reads. Async variants: `detect_server_async`, and
`client_for(info, ...)` to build a client from a prior detection.

The generated models are pinned to one spec per family (see
`amr_client.provenance`); `connect()` warns when the target's version is far
enough away that surfaces may differ (robot: different major; fleet:
different minor).
