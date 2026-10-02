# Requesting features and fixes

This emulator is developed largely by coding agents: a weekly scraper opens
spec-update PRs on its own, and scheduled/interactive agents pick up issues
and turn them into tested pull requests. That loop is only as good as its
inputs. This file explains how to write an issue or PR so an agent can act
on it **without guessing** — the difference between a request that ships in
a day and one that stalls in clarification.

## The one rule

**Make "done" mechanically checkable.** An agent can't ask you follow-up
questions at 3 AM. If your request includes a command to run and the output
you expect, it is actionable; if it says "the fleet API feels wrong," it is
not. The best requests read like a failing test.

## Opening an issue

Use this shape (copy it into the issue body):

```markdown
## What
One sentence. E.g. "GET /mission_queue/{id} returns 200 for deleted ids;
a real MiR robot returns 404."

## Versions affected
Which tracked versions you saw it on (e.g. 3.8.1, 2.14.7), or "all".

## Reproduce
# exact commands, runnable from a fresh clone
uv run amr-emulator --mir-version 3.8.1 --no-auth &
curl -s http://127.0.0.1:8080/api/v2.0.0/mission_queue/999

## Expected vs actual
Expected: 404 {"error_code": ...}   # cite the source below
Actual:   200 {...}

## Source of truth
Link or reference to the official MiR documentation (REST API PDF section,
Fleet OpenAPI operation, or observed behavior on a real robot — say which,
and include the robot's software version if it's hardware-observed).

## Acceptance
The check that proves it's fixed, e.g. "the curl above returns 404 and a
regression test covers it across all tracked 3.x versions."
```

Notes:

- **One request per issue.** Two bugs in one issue means neither gets a
  clean branch, PR, or regression test.
- **Cite the source of truth.** The emulator follows MiR's published
  documentation, not intuition. "A real robot does X" is a great source —
  say which software version. "It would be nicer if" is a feature request;
  still fine, but say so, and expect it to be weighed against the
  emulator's rule of never inventing undocumented behavior.
- **Emulator-only features** (fault injection, latency shaping, recorder —
  anything under `/_emulator/*`) are welcome requests too. For these the
  acceptance bar replaces the MiR citation: describe the exact API you want
  and what a test would assert.
- If the scraper misbehaves (missing version, broken conversion), mention
  the `scraper-attention` label — that's the channel the pipeline itself
  uses when it needs human eyes.

## Opening a PR

PRs are welcome from humans and agents alike. The bar is the same:

- Read [CONTRIBUTING.md](CONTRIBUTING.md) — it is short and binding.
- `./Quickstart -t` passes locally before you push.
- Bug fixes include the regression test, committed failing-then-fixed.
- New behavior includes negative-path tests and holds across every tracked
  version (the conformance suite is parametrized; you don't opt in, you're
  already in).
- Never hand-edit `specs/` or `registry.json` — those land only via the
  scraper pipeline.
- Keep it small. A 100-line PR with tests merges the same day; a 2000-line
  PR queues behind a human review.

If you can't finish, open the PR as a draft with a checklist of what's left.

## What happens to your request

1. An agent triages the issue: reproduces it with your commands, confirms
   the cited source, and turns your acceptance section into a failing test.
2. The fix lands on a `fix/*` or `feat/*` branch with the test, goes through
   full CI (lint, types, conformance, adversarial, fuzz, integration across
   all tracked versions), and merges to `master`.
3. The issue closes with a link to the PR. If the agent couldn't reproduce
   or the source of truth was ambiguous, it comments with exactly what was
   missing instead of guessing — tighten the issue and it re-enters the
   queue.

The fastest way through that loop is step 0: a reproduce block that runs and
an acceptance line a test can assert.
