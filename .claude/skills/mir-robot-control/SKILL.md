---
name: mir-robot-control
description: >
  Control MiR robots (real or emulated) through the MiR REST API from plain
  natural-language commands. Use this skill whenever the user wants to drive,
  inspect, or test a MiR robot or MiR Fleet — "pause the robot", "queue the
  charging mission", "what's the battery at?", "clear the error", "send an
  order to the fleet", "inject an emergency stop", "start a robot to test
  against" — even if they never say "API" or name an endpoint. Also use it
  when a task needs a running MiR robot and none exists yet (this repo's
  emulator can provide one).
---

# MiR robot control

Translate human intent ("pause it", "run the pickup mission", "is anything
broken?") into MiR REST API calls, execute them with `curl` or `httpx`, and
report the result in the user's terms — not raw JSON dumps.

## Step 1: Resolve the target

Work out where the robot is and whether it is real:

1. **User gave a URL/host** — use it. `/api/v2.0.0/...` is a robot,
   `/api/v1/...` is a Fleet.
2. **User has a robot but no address** — scan the network for it:
   ```sh
   uv run amr-discover                    # local /24, ports 80 (real) + 8080 (emulator)
   uv run amr-discover 192.168.12.0/24    # a specific subnet
   uv run amr-discover mir.local:8080     # a specific host[:port], --json for parsing
   ```
   It returns only confirmed MiR targets with their kind and software
   version; each line's URL is ready to use. (From Python:
   `amr_client.scan_network()`; from an MCP client: the `amr_discover_robots`
   tool.)
3. **Something is already listening locally** — probe before starting
   anything new: `curl -s http://127.0.0.1:8080/` (the emulator's index
   describes itself and lists versions).
4. **Nothing running** — start an emulator from this repo:
   ```sh
   uv run amr-emulator &                          # newest robot on :8080
   uv run amr-emulator --fleet-version 1.5.0 &    # a Fleet with embedded robots
   ```
   Useful flags: `--mir-version 2.14.7`, `--port`, `--no-auth`,
   `--time-scale 60` (simulated time runs 60x wall speed — missions and
   charging keep realistic durations and timestamps but finish in seconds;
   runtime control via `PUT /_emulator/clock {"scale": N}`, prefer this
   over the older shortcuts below when timestamps matter),
   `--mission-duration 3` (seconds per mission — an `X-AMR-Mission-Duration`
   header on `POST /mission_queue` overrides it per entry).

**Then ask the target what it is — never assume a version.** The path
prefixes are constant (`/api/v2.0.0` robot, `/api/v1` fleet) across all MiR
software versions, so "version" means the software version, and the target
reports it. Probe in this order, first hit wins:

```sh
curl -s $BASE/healthz                 # {"kind":"dispatcher","versions":[...]} → multi-version
                                      #   demo: pick a mount, $BASE/<v> or $BASE/fleet/<v>
curl -s $BASE/                        # emulator index: "kind" + emulated_mir_version /
                                      #   emulated_fleet_version
curl -s -H "x-api-key: $KEY" $BASE/api/v1/system/version   # a Fleet (works on real ones)
curl -s $BASE/swagger.json            # robot serving its spec → .info.version
curl -s -o /dev/null -w '%{http_code}' $BASE/api/v2.0.0/status  # 200/401 → robot,
                                      #   version unknown; treat as newest and say so
```

All probes are unauthenticated reads — safe against real hardware. From
Python, `amr_client.connect(base_url)` / `detect_server(base_url)` run this
same handshake and return a ready client; the MCP server's
`amr_server_info` tool does it too. When versions differ structurally,
`GET /_emulator/diff?from=<v>&to=<v>` (dispatcher) shows exactly what
changed between two tracked versions.

**Real vs emulated matters.** A MiR is a 100+ kg vehicle: against real
hardware, confirm before any state-changing call (PUT/POST/DELETE), never
inject faults or clear the mission queue unprompted, and say what you are
about to do first. Against the emulator, act freely. Treat any non-localhost
target as real unless the user says otherwise.

## Step 2: Authenticate

**Robot API** — MiR Basic auth is *not* standard Basic: the password is
replaced by its lowercase SHA-256 hex digest before base64 encoding.
Factory default account is `distributor` / `distributor`.

```sh
USER=distributor PASS=distributor
TOKEN=$(printf '%s:%s' "$USER" "$(printf '%s' "$PASS" | shasum -a 256 | cut -d' ' -f1)" | base64)
curl -s -H "Authorization: Basic $TOKEN" http://127.0.0.1:8080/api/v2.0.0/status
```

**Fleet API** — a single header: `x-api-key: <key>` (emulator default:
`distributor`).

A 401 means the token derivation or account is wrong — fix that; never retry
a loop against a real robot (accounts can lock).

## Step 3: Map intent to calls

Common intents, robot API (prefix every path with `/api/v2.0.0`):

| Intent | Call |
|---|---|
| "how's the robot / battery / where is it" | `GET /status` — read `state_text`, `battery_percentage`, `position`, `mission_text`, `errors` |
| "pause" / "stop what you're doing" | `PUT /status {"state_id": 4}` |
| "resume" / "continue" / "ready" | `PUT /status {"state_id": 3}` |
| "manual control" | `PUT /status {"state_id": 11}` |
| "clear the error" | `PUT /status {"clear_error": true}` |
| "rename it" / "move it to x,y" | `PUT /status {"name": ...}` / `{"position": {"x":, "y":, "orientation":}}` |
| "what missions exist" | `GET /missions` |
| "create a mission" | `POST /missions {"name": ..., "group_id": ...}` — `group_id` is required; real robots want a guid from `GET /mission_groups`, the emulator takes any string |
| "run/queue mission X" | find its guid in `GET /missions` (match by `name`), then `POST /mission_queue {"mission_id": "<guid>"}` |
| "what's queued / is it done" | `GET /mission_queue` (or `/mission_queue/{id}`) — `state` walks Pending → Executing → Done |
| "cancel everything" | `DELETE /mission_queue` |
| "cancel job N" | `DELETE /mission_queue/{id}` |
| "read/set PLC register N" | `GET /registers/{n}` / `PUT /registers/{n} {"value": ...}` |
| "set the battery / simulate charging" (emulator only) | `PUT /_emulator/battery {"percentage": 80, "charging": true, "target": 95}` — no `/api` prefix; on a real robot charging happens via its charge mission, poll `GET /status` |

Fleet API (prefix `/api/v1`): `GET /robots`, `GET|PATCH /robots/{id}`,
`POST /serial-order` (body below), `GET|DELETE /serial-order/{id}`,
`GET /order`, `GET /order/{id}`, `GET /site/mission`,
`GET /system/version`. A serial order dispatches missions to a robot:

```json
{"serial-order": {"robot-id": "<optional>", "priority": "Medium",
  "phases": [{"mission-id": "<guid from GET /site/mission>"}]}}
```

Full endpoint details, response fields, and emulator-only test surfaces
(fault injection, battery control, session isolation, latency shaping,
version diff): read [references/endpoints.md](references/endpoints.md).

**"Give me a report / dashboard / how did the day go"** — don't hand-roll
it; generate the standing dashboard (current-status indicators, daily
trend, descriptive action timeline) from official endpoints only:

```sh
uv run amr-report http://127.0.0.1:8080 -o report.html   # robot or fleet, auto-detected
```

Python: `amr_client.report.write_report(url, path)`; MCP: the
`amr_generate_report` tool. Read-only API traffic, so it is safe against
real hardware; works on any tracked software version.

## Step 4: Execute and report

- Verify connectivity with a cheap `GET /status` (robot) or
  `GET /api/v1/robots` (fleet) before acting on the real intent.
- After a state-changing call, **read back** (`GET /status`,
  `GET /mission_queue/{id}`) and report the observed state, not the request
  you sent. "Mission 'Charge' is Executing, battery 34%" — not a JSON blob.
- Mission ids and register values come from the API, never from memory.
  If a named mission doesn't exist, list what does and ask.
- Waiting for a mission: poll `GET /mission_queue/{id}` until `state` is
  `Done` (or `Aborted`); on the emulator each mission takes
  `--mission-duration` seconds (default 10) — divided by the `/_emulator/clock`
  scale, if one is set.

## Multi-robot / test isolation (emulator only)

Send `X-AMR-Session: <name>` (1–64 chars of `[A-Za-z0-9._-]`) on every
request to get a private robot/fleet instance per session id — parallel
tests never see each other's state. Keep the header consistent across a
scenario or the state "disappears". Sessions are LRU-capped at 256 per
process; past that the oldest silently resets — don't churn ids in big
simulations.

On a fleet, embedded robots have no port of their own: reach their fault
and battery surfaces through the chaos proxy,
`PUT /_emulator/robots/{robot-id}/faults` / `.../battery` (fleet
`x-api-key` auth, robot body/errors verbatim).
