# Developer-experience roadmap

What integrators building against MiR robots need from this project, in the
order we intend to ship it. Open items carry their acceptance bar so "done"
is testable, not vibes; completed work lives in git history, not here.

North star: [Stripe's API documentation](https://docs.stripe.com/api) — the
reference bar for developer experience. Applied here: versioned surfaces
where the picker switches *everything*, plain-language actions over raw
endpoints, and interfaces generated from the source of truth rather than
hand-maintained. (Per-language code samples are back by explicit request:
cURL/Python/JavaScript/Go/Rust from one persisted dropdown, on the endpoints
intro and mirroring the live console request.)

## Now

- [ ] **Publish `mir-client` to PyPI.** The SDK is generated, gated, and
      contract-tested; `release.yml` builds attested wheels and has a
      publish step waiting on credentials. BLOCKED on a PyPI-side action
      only a maintainer can take: register the project and configure
      trusted publishing (OIDC) — preferred over a long-lived
      `PYPI_API_TOKEN`, per the note in the workflow. Acceptance:
      `pip install mir-client` in a clean venv, drive a local emulator with
      `robot_client()`.

## Next

- [ ] **Version-aware fix suggestions.** The pitch is "it manages the
      versions so you don't have to" — today that means *testing* against
      every tracked version; next it should mean *fixing*. When a request
      targets one version but its shape matches another (renamed field,
      moved endpoint, changed status), detect the mismatch and propose the
      corrected request, driven by the existing
      `GET /_emulator/diff?from=&to=` rather than new heuristics. Surface it
      in the console (and eventually as a response header/annotation).
      Acceptance: send a 2.x-shaped request against a 3.x target where the
      diff shows a rename, and the console suggests the 3.x-correct request
      with the specific field/endpoint change cited from the diff.

- [ ] **Persist emulator state.** Session robot state (mission queue, PLC
      registers, status writes) is in-memory and resets on cold start. Give
      a session an opt-in durable store so a robot key survives restarts —
      the browser already persists the key itself; the server should be able
      to persist what that key points at. Acceptance: enqueue a mission,
      restart the emulator, reconnect with the same `X-MiR-Session`, and the
      queue is still there.

- [ ] **Cart / hook modeling.** `hook_status` currently always reports
      `available: false, cart_attached: false`, so "pick up the cart"
      succeeds by mission accounting with no physical confirmation channel
      (surfaced while driving the emulator as an operator). Source of truth
      first: pin the hook state machine to the official MiR250 Hook docs.
      Acceptance: a pickup mission at a cart position flips
      `cart_attached` with a spec-shaped cart document, and a drop-off
      clears it.

- [ ] **Richer reporting.** `mir-report` ships current status, one daily
      trend, and the action timeline. Next: per-mission-kind breakdowns,
      battery history (sampled via the status WebSocket), and multi-day
      trends once `/statistics/distance` has history to show. Acceptance:
      a report over a multi-day emulator run charts each day separately
      and groups timeline entries by mission kind.

## Continuous improvement

Standing quality debt from the 2026-08 hardening campaign. The campaign
fixed 10 production bugs and left 39 torture tests behind, but everything
below is what separates "passes its own suite" from production-worthy.

- [ ] **Close the conformance loop externally (VDA 5050).** Passing our
      own torture suite proves consistency, not correctness — the emulator,
      the adapter, and their tests share assumptions, and the one live
      validation so far (master control → adapter → mir-emulator) was
      in-house on both ends. Research independent open-source
      master-control implementations, pick one, and run it against
      `vda5050-emulator` for each supported spec version. Acceptance: an
      external implementation drives a full order lifecycle (dispatch →
      running → finished, plus a cancel) against the emulator with zero
      validation failures on either side, reproducible via a documented
      script or CI job.
      *Progress 2026-08-16: the MASTER direction is closed —
      `interop/otto-vda5050/` runs `vda5050-master` against the unmodified
      OTTO/InOrbit/Ekumen connector (robot side) with full lifecycle +
      stitched updates and zero validation failures (three upstream
      connector bugs documented in its README, issue-ready for
      inorbit-ai/ros_amr_interop). The emulator direction still needs an
      external MASTER; best candidate found: NVIDIA
      `isaac_mission_dispatch` (VDA5050-compatible dispatch service).
      MassRobotics is closed both ways day-one: `interop/massrobotics/`
      validates the new `massrobotics-emulator` fleet against the official
      Ajv reference receiver.*

- [ ] **File the OTTO connector bugs at inorbit-ai/ros_amr_interop.**
      Three found by `interop/otto-vda5050/` (details in its README):
      required-in-practice `nodePosition.theta`; ONLINE before the
      controller can receive orders; MQTT thread death on any schema-valid
      2.0.0 instant action (`actionName` kwarg). Acceptance: one issue per
      bug, URLs recorded in the interop README; the cancelOrder
      expected-divergence probe already fails loudly when the fix lands.

- [ ] **File the upstream schema defects at VDA5050/VDA5050.** We carry
      documented normalizations for the defects recorded in
      `packages/vda5050-emulator/src/vda5050_emulator/schemas/registry.json`
      (3.0.0 factsheet trailing commas, `mobileRobotKinematic(s)`
      required/property mismatch, string-typed pause/cancel booleans,
      2.1.0 unsatisfiable `blockingTypes` enum, vacuous 2.0.0 factsheet
      schema). Acceptance: one upstream issue per defect, its URL recorded
      next to the corresponding normalization in the registry, so the
      weekly sync tells us when a normalization can be retired.

- [ ] **Performance baseline before performance work.** "Performant" is
      currently untested — no numbers on the hand-rolled asyncio MQTT
      broker, concurrent-robot fan-out, or memory over a long soak.
      Add a repeatable bench script (fixed seed, pinned message mix)
      before optimizing anything. Acceptance: one command reports p50/p99
      publish→receive latency and messages/sec at N concurrent robots,
      plus flat memory over a multi-hour soak, with the numbers committed
      as the baseline to regress against.
      *Progress 2026-08-16: `scripts/bench_vda5050.py` is the one command;
      baselines committed under `docs/bench/` (10 and 50 robots, plus an
      8-minute soak). Remaining for the checkbox: a dedicated multi-hour
      soak run (`--duration 7200`) on a quiet machine.*

- [ ] **Mutation-test the torture suite.** Coverage says the 39 hardening
      tests execute the code; mutation catch-rate says whether they would
      notice a regression. Run `mutmut` over the modules the campaign
      touched (fault handling, error lifecycle, order evaluator).
      Acceptance: catch rate recorded, surviving mutants triaged into
      "test added" or "mutant equivalent, noted" — no silent survivors.

## Later

- [ ] **ROS-bridge protocol emulation.** Faithful rosbridge
      subscribe/publish on :9090 plus fleet event streams — the fidelity
      projects deferred from the WebSocket status push, each needing its
      own primary-source work before any code.

- [ ] **Reference docs contingency.** We deliberately deleted our
      Stripe-style reference in favor of linking MiR's official docs. If
      MiR ever unpublishes the Fleet Swagger UI or the portal's REST API
      files, resurrect ours from the scraped registry.

## Open questions for Nick

- 2026-08-16 — **FOX Robotics emulator is blocked on a spec.** You asked
  for a FOX Robotics emulator alongside Vecna, but FOX publishes no API
  artifact at all — no developer docs, no swagger, no interop-standard
  membership (searched foxrobotics.com, press, VDA5050/MassRobotics
  ecosystems; "FoxAPIs" is an unrelated company). Per the don't-fabricate
  rule I built the Vecna emulator (MassRobotics interop, their certified
  standard) and stopped on FOX. If you have FoxBot partner/integration
  docs, drop them in and the emulator follows the arcl-emulator pattern
  (provenance registry + derived spec); otherwise say the word and I'll
  emulate the closest public stand-in instead.
