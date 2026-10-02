# Scenarios — real MiR deployments, replayed on the emulator

Each script here reconstructs a published MiR customer deployment
([mobile-industrial-robots.com/cases](https://mobile-industrial-robots.com/cases))
as a runnable exercise against this repo's emulator. They are `uv run` scripts
(PEP 723 inline deps — no project install needed; the robot-auth scripts pull
in this repo's `amr-client` by relative path, so run them from the repo) and each
one drills a different slice of the API surface, so together they double as a
guided tour: sessions, missions, the queue, faults, registers, metrics,
latency shaping, and the Fleet API.

## Run them

```sh
# robot-API scenarios share one emulator
uv run amr-emulator --mission-duration 2 &

uv run scenarios/whirlpool_lineside_loop.py
uv run scenarios/sengkang_hospital_rounds.py
uv run scenarios/denso_jit_callbuttons.py
uv run scenarios/fm_logistic_endurance.py
uv run scenarios/novo_nordisk_crowded_route.py
uv run scenarios/visteon_ondemand_carts.py
uv run scenarios/machineshop_barfeed_lathes.py

# the fleet scenario wants a fleet emulator on its own port
uv run amr-emulator --fleet-version 1.5.0 --fleet-robots 3.8.1,3.8.1,3.8.1 \
    --port 9090 --mission-duration 2 &
uv run scenarios/stellantis_fleet_dispatch.py
```

Every script uses its own `X-AMR-Session`, so they can run concurrently (and
repeatedly) without stepping on each other or on your own experiments against
the shared default robot. Environment knobs: `AMR_URL`, `AMR_FLEET_URL`,
`AMR_USERNAME`/`AMR_PASSWORD`, `AMR_FLEET_API_KEY`.

## How sessions keep users from colliding

The real MiR API has no robot identifiers in its paths because a physical
robot *is* the API host — one robot per IP. The emulator multiplexes many
virtual robots onto one port with the emulator-only `X-AMR-Session` request
header: every distinct session id gets its own fully isolated robot (battery,
name, missions, queue, faults, registers), created lazily on first use. Same
endpoint, different robots:

```sh
TOKEN=$(printf '%s:%s' distributor "$(printf distributor | shasum -a 256 | cut -d' ' -f1)" | base64)
curl -s -H "Authorization: Basic $TOKEN" -H "X-AMR-Session: alice" \
    http://127.0.0.1:8080/api/v2.0.0/status   # alice's pristine robot
curl -s -H "Authorization: Basic $TOKEN" -H "X-AMR-Session: bob" \
    http://127.0.0.1:8080/api/v2.0.0/status   # bob's — fully independent
curl -s -H "Authorization: Basic $TOKEN" \
    http://127.0.0.1:8080/api/v2.0.0/status   # no header: the shared default robot
```

Three things to know: the id is a namespace, not authentication — two clients
sending the same string share a robot; state is in-memory, so an emulator
restart wipes every session; and sessions are LRU-capped (256 per process),
so the least-recently-used session is evicted first when the cap is hit.

Each script probes `GET /` first and **refuses to run against anything that
isn't the emulator** — they inject faults and write PLC registers, which you
do not want pointed at a 100+ kg vehicle by accident.

## The scenarios

| Script | Based on | Deployment | API surface exercised |
|---|---|---|---|
| `whirlpool_lineside_loop.py` | [Whirlpool](https://mobile-industrial-robots.com/cases/whirlpool) | 3× MiR200 shuttle dryer doors on a 130 m loop; 2 active + 1 hot spare on the charger | `X-AMR-Session` multi-robot isolation, `X-AMR-Mission-Duration` (the loop outlasts the default), battery-driven spare rotation with real recharging via `/_emulator/battery` |
| `sengkang_hospital_rounds.py` | [Sengkang General Hospital](https://mobile-industrial-robots.com/cases/sengkang-general-hospital) | 37× MiR250 run sterile-instrument, pharmacy, meal, and linen workflows | FIFO mission queue, `blocked_path` (active planner error, robot keeps trying), `emergency_stop` (unclearable via API — physical reset only) |
| `stellantis_fleet_dispatch.py` | [Stellantis Caen](https://mobile-industrial-robots.com/cases/stellantis-caen) | 43 robots, ~1,000 missions/day, supervision program + MiR Fleet allocation | Fleet API: `x-api-key`, `GET /robots`, `POST /serial-order` round-robin, `GET /order/{id}` lifecycle |
| `denso_jit_callbuttons.py` | [DENSO](https://mobile-industrial-robots.com/cases/denso) | Floor-level call buttons, REST integration, wireless door I/O; 500k+ missions | PLC registers as the integration bus: buttons in, door control out, dispatcher loop |
| `fm_logistic_endurance.py` | [FM Logistic](https://mobile-industrial-robots.com/cases/fm-logistic) | One MiR200 ("Mirek"), 300 m recycling runs, 18.5 km/day, three shifts | Back-to-back cycles with `X-AMR-Mission-Duration` (loaded haul vs empty return), `moved` odometry, battery drain, low-battery guard, `GET /metrics` incl. mission counters |
| `novo_nordisk_crowded_route.py` | [Novo Nordisk China](https://mobile-industrial-robots.com/cases/novo-nordisk-china) | 5× MiR500 through the plant's busiest 100 m; people and forklifts everywhere | `blocked_path` mid-mission, error read-back and clearing, `X-AMR-Latency` timeout/retry drill |
| `visteon_ondemand_carts.py` | [Visteon](https://mobile-industrial-robots.com/cases/visteon) | 4× MiR200, on-demand tablet requests, ROEQ click-in carts, 10k units/day | Mission authoring (`POST /missions` + action chains), request bursts, `DELETE /mission_queue/{id}` cancellation |
| `dhl_parcel_hub_wcs.py` | [DHL's AMR pattern](https://www.dhl.com/us-en/home/innovation-in-logistics/logistics-trend-radar/amr-logistics.html) (no MiR-official case study) | 12 AMRs behind a warehouse control system: 120 orders in 3 waves, battery rotation, mid-shift e-stop and mission failure | 12 concurrent sessions at ~50 req/s, least-loaded dispatch, `/_emulator/battery` charge rotation, quarantine + re-dispatch, exactly-once order ledger |
| `machineshop_barfeed_lathes.py` | Classic bar-feeder machine-tending pattern (composite; no MiR-official case study) | 1 robot feeds 5 bar-fed CNC lathes from a central rod rack across a compressed production day; feeders consume at different rates | Registers as machine telemetry (magazine levels in, rack stock out), lowest-stock-first dispatch feeding a single-robot queue, per-lathe `X-AMR-Mission-Duration` (realistic 1-3 min trips) under `/_emulator/clock` 60x time scaling for shift-realistic odometry and battery, exact rod-conservation ledger + zero-starvation assertion |

## Emulator behaviors these scripts rely on (verified)

* Battery drains only while a mission executes (~0.05 %/s at patrol speed);
  it does not recharge on its own. To set a level or run a charging curve,
  use the emulator-only `PUT /_emulator/battery` surface.
* `blocked_path` raises an **active planner error** while the robot keeps
  driving and the mission clock keeps running. It models a physical cause,
  so its error reports `non_resettable: true` and `clear_error` does NOT
  remove it — only `DELETE /_emulator/faults` (the obstruction removed)
  does. Same for `battery_critical`.
* `emergency_stop` freezes state, velocity, position, battery, and the
  mission clock; `PUT /status {"clear_error": true}` has no effect, matching
  real MiR firmware — only `DELETE /_emulator/faults` (the "physical reset")
  releases it, and the mission resumes in place.
* `DELETE /mission_queue/{id}` removes the entry entirely — a later `GET`
  on it returns 404 rather than an `Aborted` record.
* Mission definitions and actions persist per session, but actions are not
  semantically simulated: `hook_status.cart_attached` stays `False` and a
  mission's runtime comes from `--mission-duration` (or the emulator-only
  `X-AMR-Mission-Duration` header on that enqueue), never from its action
  chain. On real hardware, valid `action_type`s come from
  `GET /actions` and positions from `GET /positions` — don't free-type them
  outside the emulator.
