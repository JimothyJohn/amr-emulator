# Contributing

This project is built and maintained by a mix of humans and coding agents.
Everything below applies to both — if you are an agent, treat this file as
binding instructions; if you are a human, it is the shortest path to a merged
PR. The repo is deliberately mechanical: one entry point (`./Quickstart`), one
source of truth per fact, and CI that proves claims instead of trusting them.

## Ground rules (read these first)

1. **The official MiR documentation is the source of truth, not this repo.**
   The emulator mirrors the published MiR robot REST API and Fleet Enterprise
   Integration API. Never invent an endpoint, field, enum value, or status
   code — every behavior must trace to an official spec (the files under
   `packages/mir-emulator/src/mir_emulator/specs/`), an official MiR document,
   or an explicitly emulator-only surface (everything under `/_emulator/*`).
   If MiR's docs don't say, the emulator doesn't guess.
2. **Never hand-edit spec files or `registry.json`.** Specs land via the
   scraper pipeline (`packages/mir-spec-scraper/`) so provenance and hashes
   stay honest. If a spec looks wrong, fix the converter or file an issue —
   don't patch the JSON.
3. **Determinism is a feature.** Same requests, same answers. No wall-clock
   or randomness in behaviors without going through the existing sim-clock
   machinery in `behaviors.py`. Tests mock time and seed randomness.
4. **Emulator-only surfaces are namespaced.** Anything that isn't part of the
   real MiR API lives under `/_emulator/*` (faults, battery, recorder,
   ws/status, the fleet's per-robot chaos proxy) or behind `X-MiR-*` headers
   (session isolation, latency shaping). Keep it that way so integrators
   can't accidentally depend on fiction.
5. **`scenarios/` is contract documentation.** The scenario scripts encode
   deliberate behavior decisions traced to real deployments (e.g.
   `blocked_path` does not freeze the robot — that's the Novo Nordisk
   script's whole point). Before changing emulator semantics, check whether
   a scenario pins the current behavior on purpose; prose docs drift,
   scenarios run.

## Setup

```sh
git clone https://github.com/JimothyJohn/amr-emulator.git
cd amr-emulator
./Quickstart -t     # installs uv if needed, then lint + unit + integration
```

That's the whole environment. `uv sync --locked --all-packages` is run for
you; Python ≥3.11.

## Layout

- `packages/mir-emulator/` — the emulator library (Starlette). Spec-driven
  routing in `app.py`, stateful overlays in `behaviors.py`, fleet emulation
  in `fleet.py`, auth in `auth.py`, tracked specs in `specs/`.
- `packages/mir-spec-scraper/` — portal login, listing parser, PDF→Swagger
  converter, selection rule, registry updater.
- `tests/` — cross-version conformance, adversarial, fuzz, and real-TCP
  integration suites, parametrized over every tracked version.
- `TODO.md` — the roadmap, with acceptance bars. Pick items from here or
  from issues; don't invent scope.

## Workflow

- Branch from `dev`: `feat/<topic>`, `fix/<topic>`, `chore/<topic>`.
- `master` is the public release branch. It only moves by fast-forwarding
  from `dev` (a push to it deploys the public demo) — never commit to it or
  target it with a PR.
- Conventional commits with a scope: `feat(fleet): …`, `fix(scraper): …`,
  `fix(tests): …`. Look at `git log --oneline` and match.
- One task, one branch, one direction. Unrelated changes go in a separate PR.
- PRs target `dev` and must pass CI (`ci.yml`): lint, format, types,
  coverage-gated unit + conformance + fuzz, integration, across every
  tracked version.
- Deploy-chain edits (`.github/workflows/**`, `Dockerfile`, `deploy/`) go
  via draft PR and let CI judge — never predict.

## Quality gates (what CI enforces)

```sh
uv run ruff check .            # lint
uv run ruff format --check .   # formatting
uv run ty check packages       # types
./Quickstart -u                # unit + conformance + fuzz, coverage ≥ 82%
./Quickstart -i                # real servers over TCP
```

- `ruff` and `ty` findings are fixed, not suppressed. If a rule is genuinely
  wrong for a line, a targeted `noqa` with a reason is acceptable — blanket
  ignores are not.
- Locked installs only (`uv sync --locked`). If `uv.lock` changes, the PR
  says why.

## Testing bar

The bar is not "tests pass" — it is "someone actively trying to break this
gets caught by a test, not a customer ticket."

- **Test the contract, not the implementation.** Inputs → outputs, behaviors
  → invariants. A behavior-preserving refactor must not break tests.
- **Every new endpoint or behavior ships with negative-path tests**: missing
  or malformed auth, wrong session header, oversized payloads, injection
  attempts, out-of-range ids. See `tests/` for the existing adversarial
  suite — extend it, don't fork it.
- **Bug fix → regression test first.** The test goes in failing, the fix
  makes it pass, both merge together. No bug fix merges without its
  regression test.
- **Property tests** (`hypothesis`) for input-handling code. The standing
  fuzz invariant: no input produces a 5xx or a non-JSON error body.
- **Never skip or delete a failing test to clear CI.** If a test is wrong,
  fix it deliberately and explain in the commit message.
- New behaviors must hold **across every tracked version** — the conformance
  suite is parametrized over the whole registry, and your feature runs under
  all of them.

## Dependencies

Adding a dependency is a supply-chain decision. Before `uv add`:

- Prefer stdlib or an existing dependency; most needs are 20 lines away.
- Check maintenance (release within ~12 months, triaged issues) and the
  transitive footprint (`uv tree`).
- The PR description names what the dep is for, alternatives considered, and
  the transitive footprint. Silent additions are not ready for review.

## For coding agents specifically

- Read `TODO.md` and `REQUESTS.md` before starting; acceptance bars are
  written there so "done" is testable.
- Run the session-start audit: `git status`, `git branch --show-current`.
  A dirty tree you didn't create is not yours to clean — commit it to a
  `wip/recovered-*` branch and start clean.
- Verify against the source of truth, not memory: grep this repo, read the
  spec files, run the emulator and `curl` it. A confident wrong answer costs
  more than a slow right one.
- Scoped-down PRs merge fast. If the task is ambiguous, open an issue with
  your proposed acceptance criteria instead of guessing.

## Security

See [SECURITY.md](SECURITY.md) for the threat model, hard limits, and how to
report a vulnerability. The short version: locked installs, SHA-pinned
actions, least-privilege workflows, and every input path adversarially
tested. Security fixes follow the regression-test-first rule with the test
demonstrating the exploit.
