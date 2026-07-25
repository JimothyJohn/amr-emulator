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

## Later

- [ ] **ROS-bridge protocol emulation.** Faithful rosbridge
      subscribe/publish on :9090 plus fleet event streams — the fidelity
      projects deferred from the WebSocket status push, each needing its
      own primary-source work before any code.

- [ ] **Reference docs contingency.** We deliberately deleted our
      Stripe-style reference in favor of linking MiR's official docs. If
      MiR ever unpublishes the Fleet Swagger UI or the portal's REST API
      files, resurrect ours from the scraped registry.
