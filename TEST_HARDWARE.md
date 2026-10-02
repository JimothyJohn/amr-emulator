# Hardware test plan

What to run the first time this repo is connected to a real MiR robot (and
MiR Fleet, if there is one). Two goals:

1. **Fidelity.** Find every place the emulator disagrees with a real robot
   on the same software version, and turn each into a regression test.
2. **Tooling.** Prove `mir-client`, `mir-discover`, `mir-report`, `mir-mcp`
   and `mir-vda5050-adapter` work against hardware, which so far they have
   only been asserted to.

Same convention as `TODO.md`: every phase has a pass bar. Phases are
ordered by risk; do not skip ahead. Phases 0, 1 and 5 never move the
robot. Phase 2 writes but should not move it. Phases 3, 4 and 8 move a
100+ kg vehicle.

## What this repo can and cannot tell you beforehand

Everything the emulator does traces to MiR's published API definitions
(`CONTRIBUTING.md`, rule 1). The definitions say what the *shapes* are.
They say very little about behaviour, and the behaviour the emulator
implements is, today, reasoning from documents — none of it has been
observed on hardware by this project. Treat the list below as hypotheses
this plan exists to test, not as facts about real robots:

- Auth: `Authorization: Basic BASE64(user:SHA-256-hex(password))`.
  Documented in one of nine tracked specs (`FEEDBACK.md` §1.5).
- `PUT /status {"state_id": 3|4|11}` semantics, and which other fields a
  robot accepts or silently ignores.
- `PUT /status {"clear_error": true}` does not release an emergency stop.
- `DELETE /mission_queue/{id}` removes the entry (later `GET` → 404)
  rather than leaving an `Aborted` record.
- `POST /missions` requires an existing mission-group guid on a real robot.
- List endpoints whose spec schema is a single object: which shape a real
  robot answers with.
- Error body shape and status codes for validation failures, unknown ids,
  wrong methods.
- A robot serves `GET /swagger.json` (the discovery handshake's fourth
  probe relies on it; the pinned 3.5.4 spec came from somewhere, but which
  versions serve it is unknown).
- Account lockout after repeated 401s (the control skill warns about it;
  no source is cited).
- A robot's status push is rosbridge on :9090 (`TODO.md`, "Later"). The
  emulator's `/_emulator/ws/status` is its own invention and has no
  hardware counterpart to compare against.

No part of the test suite can be pointed at a base URL today:
`tests/conftest.py` builds the app in-process with `TestClient`, and
`tests/test_integration.py` boots its own local server. Every scenario in
`scenarios/` probes `GET /` and **refuses to run against anything that is
not the emulator** — correctly, since they inject faults and write PLC
registers. So the comparison harness in phase 1 has to be written; it does
not exist yet (see "Tooling to build first").

## Before going near the robot

### Collect (in a gitignored `.env.hardware`, never in the repo)

| Item | Why |
|---|---|
| Robot model (MiR100/200/250/500/600/1350…) and top module (hook, shelf lift, none) | Specs are converted from the MiR250 PDFs; other models may differ |
| Software version, exactly as the robot reports it | Decides which emulator version is the comparison target, and whether it is tracked at all |
| Robot IP, and how you reach it (robot's own WiFi AP, site WiFi, cable) | |
| An API account and its role | Use a dedicated account for testing if one can be created; note its permission group |
| Whether the robot is under MiR Fleet control | A fleet-managed robot may reject or override direct commands — unknown; see open questions |
| Fleet URL, version and an API key, if testing Fleet | |
| Who owns the robot and who is physically present | |
| A site-approved test mission and a test area | Phase 3 queues only missions the owner names |

```sh
# .env.hardware — gitignored, mode 600, never pasted into an issue
MIR_URL=http://<robot-ip>
MIR_USERNAME=<account>
MIR_PASSWORD=<password>
```

`MIR_URL`, `MIR_USERNAME`, `MIR_PASSWORD` are the names `scenarios/` and
the adapter already read; `mir-mcp` reads `MIR_ROBOT_URL` for the address.
`.env.hardware` is already ignored (`.gitignore`: `.env.*`; confirm with
`git check-ignore -v .env.hardware`). `hardware-runs/` is **not** ignored
yet — add it to `.gitignore` in its own commit before the first capture.

Shell setup used by every command below:

```sh
set -a; . ./.env.hardware; set +a
TOKEN=$(printf '%s:%s' "$MIR_USERNAME" "$(printf '%s' "$MIR_PASSWORD" | shasum -a 256 | cut -d' ' -f1)" | base64)
API="$MIR_URL/api/v2.0.0"
OUT=hardware-runs/$(date +%Y%m%d)        # gitignored; raw captures stay local
mkdir -p "$OUT"
```

Never run with `set -x`, and never echo `$TOKEN` — it is a reusable
credential, not a hash of one.

### Safety preconditions (physical robot)

Hard requirements, not suggestions. If any is not met, stop at phase 1.

- The robot's owner has agreed to the test and to each phase that writes.
- A person who knows this robot is **physically present, with line of
  sight**, for phases 2–4 and 8. Nobody runs motion phases remotely.
- An emergency stop is within that person's reach, and they have pressed
  and released it once today to confirm it works.
- The area is clear and coned off for phases 3, 4, 8. No payload, no cart,
  nothing on the top module.
- The robot is **not in production**: its queue is empty, it is not
  assigned fleet orders, and nobody is waiting on it.
- Battery above 40% at the start of any motion phase.
- You know the robot's real state before every write: read `GET /status`
  first, and record it, so every phase can put it back.
- One writer. No other script, dashboard, PLC or fleet is commanding the
  robot during the test.
- Read-only first. Phase 1 completes and is reviewed before any write.
- No retry loops on 401 or 5xx against hardware. One attempt, read the
  answer, think.
- Nothing from `/_emulator/*` is ever sent to the robot on purpose except
  the single 404 check in phase 1.
- This plan does not replace the robot's user guide, the site's risk
  assessment, or the commissioning engineer's judgment. Where they
  disagree with this file, they win.

### Tooling to build first

Needed before phase 1, each as its own PR with tests against the emulator:

- [ ] **`scripts/hw_sweep.py` — read-only capture.** Given a base URL and
      credentials, issue `GET` for every parameterless `GET` operation in
      the matching spec, then for `{id}`/`{guid}` paths using ids harvested
      from the list responses, and write one JSON record per request:
      method, path, status, response headers, body. Hard-coded to `GET`
      only; refuses any other method. Rate-limited (default 2 req/s),
      sequential, no retries. Acceptance: run against a local emulator, it
      covers every `GET` operation in the spec and issues zero non-`GET`
      requests (asserted by a test that counts methods at the transport).
- [ ] **`scripts/hw_diff.py` — structural comparison.** Takes two captures
      (robot, emulator at the same version) and reports per operation:
      status mismatch; body failing the spec's response schema (reuse the
      validation `tests/test_conformance.py` does); fields the robot sends
      that the spec does not declare; declared fields the robot omits;
      list-vs-object shape; header differences (`Content-Type`, caching,
      CORS, server). Values are compared by type, not content. Acceptance:
      two captures of the same emulator diff empty; a hand-edited capture
      produces each finding class.
- [ ] **Redaction in the capture path**, not after it (see "Data capture").
- [ ] **Decide the exclusion list.** Some `GET`s are not harmless on a real
      robot: downloads and exports (in 3.8.1: `/log/error_reports/{id}/download`,
      `/sessions/{guid}/export`, `/system/setup/sick_configs/{guid}/download`,
      `/hw/export`), streams (`/sounds/{guid}/stream`), and anything
      whose `GET` has side effects. The operation list comes from the spec
      (`uv run mir-emulator --mir-version <v> --export swagger2`); review
      it by hand once and commit the exclusions with a reason each.
      Acceptance: the list is in the script, reviewed against the spec for
      the robot's version.

## Phase 0 — connect and identify (no auth, no writes)

```sh
uv run mir-discover "<robot-ip>"            # one host; ports 80 and 8080
uv run mir-discover "<subnet>/24" --json    # only with the network owner's OK
curl -s -o /dev/null -w '%{http_code}\n' "$API/status"   # expect 401 without auth
```

```python
from mir_client import detect_server
info = detect_server("http://<robot-ip>")
print(info.kind, info.version)
```

Record: which handshake probe identified the robot (`/healthz`, `/`,
`/api/v1/system/version`, `/swagger.json`, bare `/status`), the reported
kind and version, and the raw status code of each probe.

Caution: `detect_server()` sends `x-api-key: distributor` on its Fleet
probe unless told otherwise, and `mir-discover` sweeps a /24 by default.
Against a real Fleet that probe is a failed authentication attempt; on a
plant network a sweep is a port scan. Scan a single host unless the network
owner has agreed.

Pass: the robot is found, `kind` is `robot`, and the version is either
reported or correctly reported as unknown. If the version is unknown, read
it from the robot's own UI and record that the handshake could not.

Decision point: **is the robot's version tracked?** (`mir-emulator --help`
lists them.) If yes, compare against that version. If no, compare against
the nearest tracked patch in the same minor line, say so in the results,
and expect noise.

## Phase 1 — read-only sweep, diffed against the emulator

Start the comparison target:

```sh
uv run mir-emulator --mir-version <robot-version> --port 8080
```

First request, by hand, before any script:

```sh
curl -s -D "$OUT/status.headers" -H "Authorization: Basic $TOKEN" "$API/status" > "$OUT/status.json"
jq 'keys' "$OUT/status.json"
```

Then the sweep (once `scripts/hw_sweep.py` and `hw_diff.py` exist) against
the robot and against the emulator, and the diff.

Also by hand, one request each:

```sh
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Basic $TOKEN" "$MIR_URL/swagger.json"
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Basic $TOKEN" "$MIR_URL/_emulator/faults"   # expect 404
curl -s -H "Authorization: Basic $TOKEN" "$API/does_not_exist"            # 404 body shape
curl -s -H "Authorization: Basic $TOKEN" "$API/missions/not-a-guid"       # unknown-id body shape
curl -s -H "Authorization: Basic $TOKEN" "$API/registers/1"
curl -s -H "Authorization: Basic $TOKEN" "$API/metrics" | head -20
```

If the robot serves `/swagger.json`, save it: a second machine-readable
official spec is the most valuable single artifact this plan can produce
(today 3.5.4 is the only one, and it is the PDF converter's sole oracle).
Diff it against the converted spec for that version with the scraper's
existing structural diff.

Record: the full capture (local only), the diff report, response time per
request.

Pass bar, per operation:

| Finding | Classification |
|---|---|
| Robot status code is not one the spec declares | MiR spec bug → `FEEDBACK.md` |
| Robot body fails the spec's response schema | MiR spec bug → `FEEDBACK.md`; emulator follows the robot only if we decide to model it |
| Emulator status ≠ robot status, robot matches spec | **emulator bug** |
| Emulator shape ≠ robot shape (list vs object, missing/extra field), robot matches spec | **emulator bug** |
| Error body shape differs (emulator returns `error_code`…) | **emulator bug** — error bodies are where client code breaks |
| Header differences (`Content-Type`, charset) | emulator bug if a client could observe it |
| Values differ | expected; not a finding |

Phase passes when every operation is classified and every emulator bug has
an issue. It does not need zero findings.

## Phase 2 — reversible writes, no motion

Owner present. Robot in **Pause** (set from its own UI, so the first write
is not ours). Each step: read, write, read back, restore, read again. One
at a time; stop at the first surprise.

| Step | Write | Restore | Compares against |
|---|---|---|---|
| 2.1 Pause while already paused | `PUT /status {"state_id": 4}` | — | status code, response body shape |
| 2.2 Invalid state | `PUT /status {"state_id": 999}` | — | emulator answers 400 with the valid choices |
| 2.3 Unknown field | `PUT /status {"not_a_field": 1}` | — | emulator ignores it |
| 2.4 Empty / malformed body | `PUT /status` with `{}` and with `{` | — | error body shape |
| 2.5 Register write | `PUT /registers/<n> {"value": 1}` on a register the owner confirms is unused | write the original value back | read-back value and type (int vs float) |
| 2.6 Create a mission | `POST /missions` with a `group_id` from `GET /mission_groups`; name prefixed `hwtest-` | `DELETE /missions/<guid>` | response fields vs spec; the read-back asymmetries in `references/endpoints.md` |
| 2.7 Mission without `group_id`, and with a made-up one | `POST /missions` | — | emulator: 400 without it, accepts any string with it |
| 2.8 Create a position | `POST /positions` on the active map, name prefixed `hwtest-` | `DELETE /positions/<guid>` | whether the response omits `pos_x`/`pos_y` |
| 2.9 Enqueue unknown mission | `POST /mission_queue {"mission_id": "<random guid>"}` | — | emulator: 400 |
| 2.10 Wrong method | `POST /status`, `DELETE /status` | — | emulator: JSON 405 with `error_code` |

```sh
curl -s -H "Authorization: Basic $TOKEN" "$API/status" | jq '{state_id, state_text, mission_queue_id, errors}'
curl -s -X PUT -H "Authorization: Basic $TOKEN" -H 'Content-Type: application/json' \
     -d '{"state_id": 4}' -w '\n%{http_code}\n' "$API/status"
```

Do **not** in this phase: write `position` (relocalizes the robot), `map_id`,
`mode_id`, `name`, `serial_number`; touch `/settings`, `/wifi`, `/users`,
`/hw_config`, `/software`, sessions, or anything that reboots, factory
resets, or clears site data. Those stay untested unless the owner asks for
them specifically.

Cleanup check, mandatory before leaving: `GET /missions` and
`GET /positions` contain nothing prefixed `hwtest-`; the register holds its
original value; `GET /status` matches the phase-start record.

Pass: every step's status and body shape matches the emulator, or is
classified as in phase 1; the robot ends exactly as it started; it did not
move.

## Phase 3 — missions and motion

Area clear, owner at the e-stop. Only a mission the owner names — never one
authored by this plan, and never the `hwtest-` mission from 2.6 (it has no
actions; what a real robot does with an empty mission is unknown).

| Step | Action | Observe |
|---|---|---|
| 3.1 | `POST /mission_queue {"mission_id": "<owner's mission guid>"}` with the robot in Pause | Entry state while paused; the `id` type and monotonicity |
| 3.2 | `PUT /status {"state_id": 3}` | Transition Pending → Executing; `state_id`/`state_text`, `mission_text`, `mission_queue_id` in `/status` |
| 3.3 | Poll `GET /status` and `GET /mission_queue/<id>` at 1 Hz | Field names, state strings, timestamp format (`started`, `finished`) and timezone |
| 3.4 | `PUT /status {"state_id": 4}` mid-mission, then `3` | Does it resume where it stopped (emulator: yes)? |
| 3.5 | Let it finish | Final state string; whether the entry stays listed |
| 3.6 | Queue two, then `DELETE /mission_queue/<second id>` | Then `GET` it: 404 (emulator) or an `Aborted` record? |
| 3.7 | Queue one, `DELETE /mission_queue` while executing | What the robot does physically; resulting entry states |
| 3.8 | `uv run mir-report "$MIR_URL" --username "$MIR_USERNAME" --password "$MIR_PASSWORD" -o "$OUT/report.html" --json` | Renders without error; numbers match the robot's UI |

Record the whole status poll as a time series (local). It is the reference
for the emulator's mission simulation: real state sequence, real field
values during transitions, real battery drain per minute, real
`distance_to_next_target` behaviour.

Pass: the state *sequence* and every state *string* match the emulator's;
`DELETE` semantics match; `mir-report` works unmodified. Durations and
positions are expected to differ.

## Phase 4 — faults the emulator simulates

The emulator injects `emergency_stop`, `localization_lost`,
`battery_critical`, `blocked_path`. On hardware each has to be caused
physically, by the owner, and only the ones they are willing to cause.
`battery_critical` is not worth draining a battery for — skip it unless the
robot happens to be low.

| Fault | How (owner does it) | What to capture | Emulator claim under test |
|---|---|---|---|
| Emergency stop | Press the e-stop while idle; then again mid-mission | `/status` before, during, after release: `state_id`, `state_text`, `errors[]` (code, module, description) | State freezes; `clear_error` does **not** release it; mission resumes in place after physical reset |
| `clear_error` during e-stop | `PUT /status {"clear_error": true}` | status code, effect | No effect, still 200 |
| Blocked path | Owner places a soft obstacle on the route mid-mission | `errors[]`, whether the mission clock keeps running, `state_id` | Robot keeps trying; error is not clearable via API |
| Lost localization | Only if the owner has a routine way to do it | `state_id` (emulator: 12), `errors[]`, whether `clear_error` resets it | `clear_error` resets it |
| Protective stop / manual brake release | If it occurs naturally | everything | Not modelled; candidate new fault |

Every real `errors[]` entry is gold: the emulator's error codes and text
are, at best, spec examples. Capture them verbatim (they contain no
secrets; check for serials).

Pass: each emulator claim is confirmed or corrected. A corrected claim
changes `behaviors.py` **and** the scenario that pins it
(`CONTRIBUTING.md`, rule 5 — `scenarios/` is contract documentation).

## Phase 5 — authentication, negative paths

Read-only target (`GET /status`) throughout. **One request per case, at
least 10 seconds apart, and stop after the listed cases** — whether real
robots lock an account after repeated failures is unknown, and finding out
by locking the owner's account is not acceptable. Use the dedicated test
account, not the owner's.

| Case | Expect (emulator) |
|---|---|
| No `Authorization` header | 401 |
| Standard Basic (`curl -u user:password`, password not hashed) | 401 |
| Correct scheme, wrong password | 401 |
| Uppercase hex digest | 401 on the emulator — a real robot may differ |
| `Bearer <token>` | 401 |
| Valid token, lowercase `basic` scheme | 200 (the emulator matches the scheme case-insensitively) |
| Valid token on `/swagger.json` and on `/` | record whether auth is required there |

For each: status code, `WWW-Authenticate` header (present? what realm?),
body shape. Then one valid request to confirm the account still works.

Also record: does the robot answer on HTTPS; does HTTP redirect; is there a
session cookie; do CORS preflights (`OPTIONS`) get answered and how.

Pass: the emulator's auth decisions match case for case. Any mismatch is an
emulator bug with a regression test in `packages/mir-emulator/tests/test_auth.py`.

## Phase 6 — timing, rate and push

No stress testing against hardware. This phase measures; it does not push.

- Latency of `GET /status`, 60 samples at 1 Hz: p50/p95. Feeds a realistic
  default for `--latency-ms`.
- How fresh is `/status`? Poll at 5 Hz for 20 s while the robot moves; note
  how often `position` actually changes.
- Sequential `GET /missions` ×20 at the same pace: any 429, any slowdown,
  any `Retry-After`? Stop at the first non-200.
- Two concurrent `GET /status` requests (not more): both answered?
- Timestamp formats across endpoints, and whether they are robot-local or
  UTC.
- Push: does anything listen on :9090 (`nc -z <robot-ip> 9090`)? If so,
  note it and stop — rosbridge emulation is a separate project
  (`TODO.md`, "Later") and connecting a client is out of scope here.
  Confirm the robot has no `/_emulator/ws/status` (it should not; phase 1
  already saw the 404).

Pass: numbers recorded. Nothing here gates anything; it calibrates
defaults and tells us whether a rate-limit behaviour needs modelling.

## Phase 7 — MiR Fleet (only if one exists)

Fleet moves multiple robots. Everything in "Safety preconditions" applies
to every robot the fleet can reach, and the fleet's owner agrees to each
write.

```sh
curl -s -H "x-api-key: $MIR_API_KEY" "$MIR_FLEET_URL/api/v1/system/version"
curl -s -H "x-api-key: $MIR_API_KEY" "$MIR_FLEET_URL/api/v1/robots"
```

- 7.0 Identify: `detect_server(fleet_url, api_key=...)`; version tracked
  (1.5.0, 1.4.2, 1.3.1)?
- 7.1 Read-only sweep and diff, as phase 1, against
  `uv run mir-emulator --fleet-version <v>`. Fleet specs are MiR's own
  OpenAPI 3 documents, so spec-vs-robot disagreements here are squarely
  `FEEDBACK.md` material.
- 7.2 Auth negatives: no key, wrong key — one request each.
- 7.3 One serial order, with a mission the owner names, on one robot in a
  clear area: `POST /api/v1/serial-order`, then poll `GET /order/{id}`
  through its lifecycle. Compare the state sequence with
  `scenarios/stellantis_fleet_dispatch.py` run against the emulator.
- 7.4 Abort an order mid-flight, if the owner agrees.
- 7.5 Does a fleet-managed robot still accept direct `/api/v2.0.0` writes?
  Read-only check first (`GET /status` on the robot directly); a write only
  with the owner's say-so. The emulator's fleet drives its robots over
  their own REST API — whether real Fleet does is an assumption.

Pass: as phase 1 and phase 3, for the fleet surface.

## Phase 8 — client tooling and the VDA 5050 adapter

### SDK

```python
from mir_client import connect
from mir_client.robot.api.default import get_status

client = connect("http://<robot-ip>")   # pass the account per mir_client's signature
status = get_status.sync(client=client)
print(status.state_text, status.battery_percentage)
```

The generated models are pinned to one spec per family. The test is
whether real responses **parse**: call every generated `GET` for a
parameterless operation and record each that raises. A model that cannot
parse a real robot's answer is an SDK bug even when the emulator is right.

### MCP

Point `mir-mcp` at the robot (`MIR_ROBOT_URL`, `MIR_USERNAME`,
`MIR_PASSWORD` in the client's env; keep destructive-tool confirmation on).
Run, in order: `mir_server_info`, `mir_robot_status`, `mir_list_missions`,
`mir_mission_queue`, `mir_read_register`. Then, with the owner at the
e-stop: `mir_set_robot_state` pause/ready, `mir_queue_mission` (owner's
mission) with wait, `mir_wait_for` queue idle. `mir_manage_faults` must
fail cleanly (404 from hardware surfaced as a tool error, not a crash).
Do not run `mir_cancel_missions` without the owner's go-ahead; confirm the
elicitation prompt appears before it clears the queue.

### VDA 5050 adapter (moves the robot)

The adapter **creates positions and missions on the robot** for every
order (`mir.py: enqueue_route` → `POST /missions`, `POST /positions`,
`POST /missions/{guid}/actions`, `POST /mission_queue`) and it talks MiR
REST as of 3.8.1. Against a 2.x robot expect it to fail; record how.

```sh
uv run vda5050-emulator --robots 0 --port 1884          # broker only
uv run mir-vda5050-adapter --mir-url "$MIR_URL" \
    --mir-username "$MIR_USERNAME" --mir-password "$MIR_PASSWORD" \
    --broker 127.0.0.1:1884 --spec 2.0.0 --manufacturer hwtest --serial hw01
mosquitto_sub -h 127.0.0.1 -p 1884 -t '#' -v            # watch connection/state/factsheet
```

Note the password is on the command line here (visible in `ps`); the
adapter also reads `MIR_USERNAME`/`MIR_PASSWORD` from the environment —
prefer that and omit the flags.

- 8.1 Adapter starts, publishes `connection` ONLINE, a factsheet, and a
  `state` whose pose matches the robot's UI. Radians vs degrees is the
  thing to check — MiR speaks degrees, VDA 5050 radians.
- 8.2 One order with two nodes at coordinates the owner picks on the
  active map, a short distance apart, in the cleared area, sent from
  the `vda5050_master` library or by hand. Watch: the mission the adapter creates on
  the robot, node traversal reported in `state`, completion.
- 8.3 `startPause` / `stopPause` instant actions mid-order.
- 8.4 `cancelOrder` mid-order.
- 8.5 Cleanup: the adapter leaves its created missions and positions on
  the robot. List and delete them (`GET /missions`, `GET /positions`,
  filter by the order names), and record that as a defect to fix — an
  adapter that litters a production robot's mission list is not shippable.

Pass: a full order lifecycle with schema-valid messages both ways and the
robot physically arriving where the order said. Map-frame correctness (does
VDA `x,y` equal MiR `pos_x,pos_y` on this map?) is confirmed by eye and
tape measure, not by the software agreeing with itself.

## Data capture and redaction

Raw captures from a customer robot contain things that must not reach git,
an issue, or a chat window:

- IP and MAC addresses, hostnames, WiFi SSIDs and anything from `/wifi`.
- Serial numbers (`serial_number` in `/status`, hardware serials in
  `/system/info` and similar).
- Usernames, user records, anything from `/users`, sessions, permissions.
- Robot name, site/map names, mission and position names — they describe
  the customer's facility.
- Map data, error-report and log downloads (excluded from the sweep).
- The `Authorization` header and `x-api-key`, in requests and in any
  logged curl command line.

Rules:

- `hardware-runs/` is gitignored before the first capture
  (`.env.hardware` already is). Raw captures stay on the laptop.
- The capture script redacts at write time: drop request auth headers;
  replace the fields above with typed placeholders (`"<string>"`,
  `"<ipv4>"`), keeping structure and types — which is all the diff needs.
- What gets committed is **synthetic**: a fixture hand-built to have the
  robot's *shape* with emulator-style values, plus the diff report. Never a
  trimmed copy of the real document.
- Issues cite "observed on MiR<model>, software <version>" — the format
  `REQUESTS.md` asks for — and nothing that identifies the site.
- Before any commit from a test day:
  `git diff --cached | grep -nE '([0-9]{1,3}\.){3}[0-9]{1,3}'` and a search
  for the robot's serial and name. Unpiped, by eye.

## How findings flow back

One finding, one issue, one branch — using the `REQUESTS.md` template with
"Source of truth: observed on a real robot, <model>, <version>".

- **Emulator bug** (robot and spec agree, emulator differs): regression
  test first, failing, built from a synthetic fixture; then the fix; the
  test stays. Parametrized over the versions it applies to — hardware
  proved one version; say which, and do not silently extend the change to
  versions nobody observed unless the spec text is identical.
- **MiR spec bug** (robot contradicts its own spec): a dated,
  version-specific entry in `FEEDBACK.md`. Then decide explicitly whether
  the emulator follows the spec or the robot, and write that down next to
  the behaviour. Default: follow the robot for anything a client can
  observe, and keep a conformance exception with a comment citing the
  observation.
- **Behaviour the spec is silent on** (state sequences, error codes,
  timing): the hardware observation becomes the source of truth. Update
  `behaviors.py`, the scenario that pins it, and
  `.claude/skills/mir-robot-control/references/endpoints.md`.
- **Tooling bug** (SDK cannot parse, MCP tool crashes, adapter litters):
  fix in the package, with a test that replays the synthetic fixture.
- **Model- or version-specific difference:** record it; do not generalize
  from one robot.

When phases 1–5 are classified, replace the "hypotheses" list at the top of
this file with what was observed, and update the fidelity claims in
`README.md` and `PROMOTION.md` to say exactly what was validated on what.

## Results template

Copy per test day into `docs/validation/hardware-<model>-<version>.md`
(redacted), alongside the existing external validations.

```markdown
# Hardware validation: MiR<model>, software <version>

Date: YYYY-MM-DD · commit <sha> · emulator target <version> (tracked: yes/no)
Top module: <none/hook/…> · Fleet-managed: yes/no · Present: <roles, not names>

## Phase results
| Phase | Run | Result | Findings |
|---|---|---|---|
| 0 Identify | yes | pass | handshake probe: … |
| 1 Read-only sweep | yes | N ops compared, M findings | #issue, #issue |
| 2 Reversible writes | … | | |
| 3 Missions | … | | |
| 4 Faults | which were caused | | |
| 5 Auth | … | | |
| 6 Timing | p50/p95 status latency | | |
| 7 Fleet | n/a | | |
| 8 Tooling / adapter | … | | |

## Findings
| # | Operation | Robot | Emulator | Spec says | Class | Issue |
|---|---|---|---|---|---|---|

## Hypotheses confirmed / corrected
- …

## Not tested, and why
- …

## Robot left as found
- [ ] queue empty · [ ] no `hwtest-` missions/positions · [ ] register restored
- [ ] state matches the pre-test record · [ ] owner signed off
```

## Open questions (cannot be answered from this repo)

- Does a real robot serve `/swagger.json` at the root, and on which
  software versions?
- Does repeated 401 lock an account, after how many, and for how long?
- Exact error body shape on a real robot for 400/404/405.
- Does `DELETE /mission_queue/{id}` remove the entry or mark it aborted?
- Does a robot under MiR Fleet accept direct REST writes?
- Is there any rate limiting, and does HTTPS exist on the robot API?
- Do non-MiR250 models differ in API surface for the same software version?
- What does a robot do with a mission that has no actions?
- Is the MiR map frame directly usable as the VDA 5050 map frame, or is an
  origin/rotation transform needed per site?
- Which robot, model, and software version will this actually be run on,
  and who owns it? Everything above is written without knowing.
