# AMR Emulator

An [advin.io](https://advin.io) service — spec-faithful emulators of
autonomous mobile robot (AMR) REST APIs, starting with Mobile Industrial
Robots (MiR).

[![GitHub](https://img.shields.io/badge/GitHub-JimothyJohn%2Famr--emulator-181717?logo=github)](https://github.com/JimothyJohn/amr-emulator)
[![Live demo](https://img.shields.io/badge/Live_demo-amr--emulator.com-2ea44f)](https://amr-emulator.com/console)

Self-updating emulator of the [Mobile Industrial Robots (MiR) robot REST API](https://supportportal.mobile-industrial-robots.com/documentation/rest-api/rest-api-files/)
**and the [MiR Fleet Enterprise Integration API](https://supportportal.mobile-industrial-robots.com/support-files/manuals/MiR_Fleet_Enterprise_OpenAPI_Specification/1.5.0/index.html?urls.primaryName=MiR+Fleet+Integration+API+v1)**.
Develop and test MiR integrations against a local, spec-faithful `/api/v2.0.0`
(robot) or `/api/v1` (fleet) without owning either — across the newest four
minor lines of every major software generation.

```sh
./Quickstart -t          # lint + unit + conformance + integration
./Quickstart -s          # serve the newest tracked robot version on :8080

curl -H "Authorization: Basic $(printf '%s:%s' distributor "$(printf distributor | shasum -a 256 | cut -d' ' -f1)" | base64)" \
  http://127.0.0.1:8080/api/v2.0.0/status

uv run mir-emulator --fleet-version 1.5.0   # a MiR Fleet with two embedded robots
curl -H 'x-api-key: distributor' http://127.0.0.1:8080/api/v1/robots
```

## The fleet emulates MiR Fleet Enterprise — by driving robot emulators

`mir_emulator.fleet` embeds a configurable set of robot emulators and controls
them the way a real MiR Fleet does: **over the robots' own REST API** (auth,
validation, mission simulation — the full HTTP stack, via an in-process ASGI
transport). A `POST /api/v1/serial-order` really enqueues missions on a robot's
`/mission_queue`; order status is derived live from the robot's simulation, so
the fleet view and the robot view can never disagree. `X-MiR-Session` composes:
one session id gets an isolated fleet **and** isolated robots. Fleet specs are
MiR's official OpenAPI 3 documents, served verbatim (no PDF conversion) —
see the public [Swagger UI](https://supportportal.mobile-industrial-robots.com/support-files/manuals/MiR_Fleet_Enterprise_OpenAPI_Specification/1.5.0/index.html?urls.primaryName=MiR+Fleet+Integration+API+v1)
for the canonical reference; the emulator links to it rather than rebuilding it.

## How it stays current

1. **`scrape.yml`** runs weekly: logs into the MiR support portal, parses the
   REST API files listing (~500 PDFs, one per product per version), and
   applies the **selection rule** — *for every major release line, the
   latest patch of each of its newest 4 minor lines* (so both MiR software
   generations stay covered four API revisions deep).
2. MiR publishes the API definitions **as PDFs only** (swagger2markup +
   Asciidoctor renderings of their internal swagger doc). The scraper picks
   one robot PDF per selected version (MIR250 preferred; FLEET/HOOK are
   different APIs and excluded) and **converts it back to Swagger 2.0**
   (`mir_spec_scraper/pdf_convert.py`).
3. The converter is gated by a **correctness oracle**: MiR published exactly
   one machine-readable spec ever (3.5.4 `swagger.json`, pinned in the
   registry). Every scrape run re-converts the 3.5.4 PDF and requires zero
   structural differences (operations, parameters, response schemas,
   definition property types) against that official document.
4. New or changed specs land in
   `packages/mir-emulator/src/mir_emulator/specs/` + `registry.json` via an
   automated PR; **`ci.yml`** proves every tracked version against the full
   conformance + adversarial suite before it merges.
5. The **fleet half** of the same scrape needs no credentials: MiR publishes
   Fleet Enterprise as native OpenAPI 3 JSON at public URLs. Discovery probes
   forward from the tracked versions (new patches, minors, majors) and the
   same selection rule applies per major line.
6. **`release.yml`** builds one `mir-emulator` distribution per tracked MiR
   version: `pip install mir-emulator==3.8.1` gets a 3.8.1 robot.

### Secrets

- `MIR_PORTAL_EMAIL` / `MIR_PORTAL_PASSWORD` — portal credentials (free
  account); without them the scrape workflow no-ops with a notice.
- `OPEN_ROUTER_API_KEY` (optional) — adds an AI-generated "release impact"
  summary on top of the mechanical API changelog in scrape PRs (model:
  `anthropic/claude-sonnet-5`, override with `MIR_SUMMARY_MODEL`). Strictly
  best-effort: any failure falls back to the mechanical report.
- `PYPI_API_TOKEN` (optional) — to publish wheels from `release.yml`.

## Tracked versions

`packages/mir-emulator/src/mir_emulator/specs/registry.json` is the
authoritative list (versions, hashes, provenance, source PDF URLs). New
releases are picked up as the latest patch of each major's newest 4 minor
lines; once tracked, a minor line is permanent — it keeps updating to its
latest patch but is never dropped. Currently:

| Family | Versions | Source |
|---|---|---|
| Robot REST API 3.x | 3.8.1, 3.7.2, 3.6.7, 3.5.6 | Converted from the official MiR250 REST API PDFs |
| Robot REST API 3.x | 3.5.4 (pinned) | Official `swagger.json` — the converter's oracle |
| Robot REST API 2.x | 2.14.7, 2.13.5.4, 2.12.0.4, 2.10.5.8 | Converted from the official MiR250 REST API PDFs |
| Fleet Integration API | 1.5.0, 1.4.2, 1.3.1 | Official OpenAPI 3 JSON, served verbatim (public URLs) |

## What the emulator does

- Serves **every operation** in the loaded spec under `/api/v2.0.0`
  (289 operations across 159 paths in 3.8.1), with responses that validate
  against the spec's response schemas. Deterministic: same requests, same
  answers.
- **Stateful** where it matters: `/status` (PUT merges), `/mission_queue`
  (POST enqueues `Pending` entries with monotonic ids, DELETE clears),
  `/registers` (200 PLC registers, read/write), generic CRUD with
  create/read/update/delete semantics everywhere else. `/metrics` speaks
  OpenMetrics.
- **MiR-style auth**: `Authorization: Basic BASE64(user:SHA-256(password))`,
  default account `distributor`/`distributor` like a factory robot. Override
  with `--username/--password` or disable with `--no-auth`.
- **Made for hardening**: `/_emulator/faults` injects emergency stop, error,
  localization loss, critical battery, and blocked-path states (session-
  isolated; holding faults freeze the mission simulation); `/_emulator/battery`
  sets the battery level and runs charging curves toward a target; on a fleet,
  `/_emulator/robots/{robot-id}/{faults|battery}` proxies both surfaces to an
  embedded robot so orders can be chaos-tested in flight; `/_emulator/clock`
  runs simulated time Nx wall speed (process-wide) so missions and charging
  keep realistic durations and timestamps while tests wait seconds, not
  minutes (`--time-scale` at startup); `X-MiR-Latency`
  delays any response for timeout testing; `X-MiR-Mission-Duration` gives one
  queue entry its own runtime (real routes are not uniform);
  `/_emulator/diff?from=&to=` on the dispatcher reports structural API changes
  between tracked versions.
- **Middleware-ready**: serves its own API definition at `/swagger.json`
  (Swagger 2.0, verbatim) and `/openapi.json` (OpenAPI 3.0, converted and
  round-trip-validated) so SDK generators and contract-testing tools can point
  straight at it; `--cors` for browser dashboards; `--export openapi3` to dump
  the definition; `Dockerfile` + `compose.yaml` for CI service stacks
  (`docker compose up` → MiR 3.8.1 on :8080 and 2.14.7 on :8081).

```python
from mir_emulator import create_app, supported_versions

app = create_app("3.8.1")   # ASGI app: run under uvicorn, or hit with httpx/TestClient
```

## Layout

- `packages/mir-emulator/` — the emulator library (Starlette; spec-driven
  routes + behavior overlays). Bundles all tracked spec files.
- `packages/mir-spec-scraper/` — portal login, listing parser, selection
  rule, registry updater.
- `tests/` — cross-version conformance, adversarial/negative-path, and
  real-TCP integration suites, parametrized over every tracked version.
- `scripts/build_versioned.py` — stamps and builds one wheel per MiR version.

## Hardening

Test harness: every tracked version runs the conformance suite (every
operation answered with a declared status, every GET body validated against
its response schema), an adversarial suite (auth bypass, injection, traversal,
oversized payloads, concurrency races), and a deterministic hypothesis fuzz
suite whose invariant is *no input produces a 5xx or a non-JSON error* — plus
real-TCP integration tests and an offline test of the full scraper state
machine (pinning, dropping, broken-file fallback). CI gates coverage at 82%
offline; the PDF converter's full-document path is gated live by the 3.5.4
oracle on every scrape.

Supply chain: SHA-pinned actions, `permissions: {}` + least-privilege jobs,
locked installs everywhere, Dependabot (uv + actions), CodeQL, PR dependency
review, and build-provenance attestations on release wheels. Details and hard
limits: [SECURITY.md](SECURITY.md).

Self-improvement loop: the weekly scrape opens PRs whose body is an **API
changelog** (added/removed/changed operations and definitions), re-validates
the converter against the pinned oracle first, survives individually broken
portal files by falling back to the last good spec of that major, and files a
`scraper-attention` issue whenever anything needed human eyes — a new major,
a new file format, or a PDF shape the converter can't parse cleanly.

## Dependencies (why each exists)

Runtime: `starlette` + `uvicorn` (ASGI routing/serving), `jsonschema`
(request/response validation against the spec), `pyyaml` (YAML specs),
`httpx` (scraper HTTP + test client), `pdfplumber` (scraper only: the portal
publishes PDFs, and its ruled-table extraction is what makes the PDF→swagger
conversion reliable). Dev: `pytest`, `hypothesis` (property tests on the
input-handling paths), `ruff`, `ty`.

## License

[MIT](LICENSE) — use it freely, commercially or not; the only ask is that the
copyright notice stays with the code. If this emulator saves you robot time,
a mention is appreciated.
