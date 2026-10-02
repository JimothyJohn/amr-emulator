# Promotion plan

How MiR users and software developers find this project, get a first
request answered, and keep using it. Same convention as `TODO.md`: open
items carry an acceptance bar so "done" is checkable. Nothing here changes
code by itself — each item that does becomes its own branch and PR.

## Where we stand (verified 2026-10-01)

Each line says what was checked. Anything not checked is marked as such.

| Fact | Status | How it was checked |
|---|---|---|
| Repo visibility | public, MIT, 0 stars, 1 fork, no releases, Discussions off, Issues on | `gh repo view --json …`, `gh release list` |
| Repo topics | **none set** | `repositoryTopics: null` in the same call |
| Repo description | "…of autonomous mobile robot REST APIs (MiR today; more brands coming)" — stale: VDA 5050, ARCL and MassRobotics already ship | same call vs. `README.md` |
| PyPI | **nothing published.** `mir-emulator`, `mir-client`, `mir-mcp`, `vda5050-emulator`, `mir-vda5050-adapter`, `massrobotics-emulator`, `arcl-emulator`, `vda5050-master`, `amr-emulator` all answer 404, so every name is also still unclaimed | `curl https://pypi.org/pypi/<name>/json` |
| `pip install mir-emulator==3.8.1` | claimed in `README.md` ("How it stays current", step 6) but not true today | PyPI 404 + `release.yml` only publishes when `PYPI_API_TOKEN` is set, and it has never run on a tag (no releases) |
| Container image | **not published anywhere.** `ci.yml` builds `mir-emulator:ci` and smoke-tests it; no workflow pushes to a registry | `grep -i "ghcr\|docker" .github/workflows/*.yml` |
| Hosted demo | up. `https://amr-emulator.com/` → 200 JSON index, `/console` → 200 HTML, `/healthz` lists 9 robot + 3 fleet versions, `/latest/api/v2.0.0/status` → 401 without auth (correct) | `curl` |
| Crawlability | `/robots.txt`, `/sitemap.xml`, `/llms.txt` all 404 (as JSON); the bare domain serves JSON, not a page | `curl` |
| Page metadata | `docs/index.html`, `landing.html`, `vda5050.html` have `<title>` and `<meta name="description">`; no Open Graph, canonical, or JSON-LD tags found | `grep` over `docs/*.html` |
| MCP registry | `mir-mcp` not listed (search for "mir" returns unrelated servers only). It cannot be listed yet either: the registry entry points at a published package | `curl "https://registry.modelcontextprotocol.io/v0/servers?search=mir"` |
| GHCR listing | **unverified** — the `gh` token lacks `read:packages`; the workflow evidence above says nothing is pushed | `gh api users/JimothyJohn/packages` → 403 |
| Search ranking, inbound links, traffic | **unverified** — nothing measured yet (see Metrics) | — |

Short version: the product is live and the work is real, but there is no
install path that does not start with `git clone`, and nothing tells a
search engine or a registry that it exists. Fix distribution before
posting anywhere — a launch post that ends in "clone the monorepo" wastes
the one shot each channel gives.

## Who is looking, and what they type

| Audience | Their problem | What they search for | What we hand them |
|---|---|---|---|
| **Integrator / automation engineer** with a MiR on order or on a busy floor (PLC, SCADA, MES/WMS people; Ignition, UR+MiR cells) | Cannot develop against a robot that is not there or is in production | "MiR REST API example", "MiR REST API authorization", "MiR API 401", "MiR mission queue POST", "MiR robot simulator" | Hosted URL that answers the same requests + the auth one-liner |
| **Software developer** building a WCS/dashboard/app on MiR or MiR Fleet | No test target for CI; version drift between robots | "MiR API mock", "MiR Fleet API sandbox", "MiR python client", "MiR openapi / swagger json" | `pip install` / container for CI, typed client, `/openapi.json` |
| **Fleet-software / master-control developer** | Needs VDA 5050 robots to drive without hardware | "VDA 5050 simulator", "VDA5050 test robot", "VDA 5050 MQTT emulator" | `vda5050-emulator` with embedded broker; external validations in `docs/validation/` |
| **Robotics platform / interop people** (ROS, Open-RMF, MassRobotics) | Adapter and conformance testing | "MiR VDA5050 adapter", "MassRobotics AMR interop test" | `mir-vda5050-adapter`, `massrobotics-emulator`, `interop/` harnesses |
| **Agent / LLM tooling developers** | Want a physical-world API that is safe to let an agent loose on | "robot MCP server", "MCP robotics" | `mir-mcp` against the hosted emulator |
| **MiR itself** (API team, partner engineering) | — | — | `FEEDBACK.md`, as a courtesy and a relationship, not a channel |

The first two rows are the request. The auth scheme is the hook: MiR Basic
auth hashes the password with SHA-256 before encoding, the spec declares it
as plain `basic`, and it is documented in one of nine tracked specs
(`FEEDBACK.md` §1.5). Public threads of people stuck exactly there exist
(e.g. the Inductive Automation forum thread "MiR 250 Robot with Rest API
need help with HTTP Post"). A page that answers "why is my MiR API call
401" and then offers a robot to try it on is the best single entry point
we can build.

## Positioning

One sentence, reused everywhere (repo description, PyPI summary, page
title, post titles):

> **A MiR robot REST API you can develop against without a robot** —
> spec-faithful, every tracked software version, free hosted endpoint or
> one command locally.

Supporting claims, each of which is already backed by something in the repo
and should link to it rather than assert it:

- Built from MiR's own API definitions, not from guesswork — 9 robot
  software versions and 3 Fleet versions (`registry.json`), refreshed
  weekly by `scrape.yml`.
- Same code, then the real robot: paths, auth, and status codes match, and
  emulator-only extras are fenced under `/_emulator/*` and `X-MiR-*`.
- Break it on purpose: e-stop, lost localization, blocked path, low
  battery, latency, 60x time.
- Not only MiR: VDA 5050 2.0.0/2.1.0/3.0.0, Omron ARCL, MassRobotics.

Do not claim hardware fidelity beyond the spec until `TEST_HARDWARE.md`
has been run. Until then the honest phrasing is "faithful to MiR's
published API definitions"; after it, "validated against a MiR<model>
running <version>" becomes the strongest line we have.

### Affiliation and trademark

"MiR" and "Mobile Industrial Robots" are MiR's marks. Required everywhere
we publish:

- A visible "independent project, not affiliated with or endorsed by
  Mobile Industrial Robots" line on the site footer, the README, and each
  package README. (Open question below: whether one exists on every page
  today was not audited.)
- Use the name descriptively ("emulator of the MiR REST API"), never as our
  brand. No MiR logo, no MiR colours or product photos.
- The specs are redistributed from MiR's support portal, whose robot API
  files sit behind a (free) login. That is a licensing question, not a
  marketing one, and it gets louder with visibility — see open questions.
- `scenarios/` cite published MiR customer case studies by company name.
  Keep them framed as "reconstructed from the public case study", linked,
  with no implication those companies use this project.
- `FEEDBACK.md` is critical of MiR's API. Keep it factual and
  version-specific (it is); never lead a post with it.

## Phase 0 — make it installable and findable

Nothing in Phase 1+ starts until these are done. Ordered.

- [ ] **Claim the PyPI names and publish.** All nine names are free today;
      that can change the day the repo gets attention. Register
      `mir-emulator`, `mir-client`, `mir-mcp`, `vda5050-emulator`,
      `mir-vda5050-adapter` first (the rest can follow), with trusted
      publishing (OIDC) rather than the long-lived `PYPI_API_TOKEN`
      `release.yml` currently expects. `release.yml` builds only
      `mir-emulator` wheels (`scripts/build_versioned.py`); the other
      packages need a build step, and `mir-mcp` and the adapter depend on
      workspace siblings that must exist on PyPI first. This subsumes the
      "Publish `mir-client` to PyPI" item in `TODO.md`. Acceptance: in a
      clean venv, `pip install mir-emulator` then `mir-emulator` serves
      `/api/v2.0.0/status` on :8080; `pip install mir-client` drives it
      with `robot_client()`; `uvx mir-mcp` starts.
- [ ] **Make the README claim true or remove it.** `pip install
      mir-emulator==3.8.1` is stated as fact. Acceptance: the command works,
      or the sentence says "from a checkout" until it does.
- [ ] **Publish a container image.** CI already builds and smoke-tests the
      `Dockerfile`; add a push to GHCR on release tags (deploy-chain edit:
      draft PR, SHA-pinned actions, job-scoped `packages: write`).
      Integrators on Windows engineering laptops and CI users want this
      more than a wheel. Acceptance: `docker run -p 8080:8080
      ghcr.io/jimothyjohn/mir-emulator` answers `/api/v2.0.0/status`, and a
      copy-paste GitHub Actions `services:` snippet is in the README.
- [ ] **Repo metadata.** Description → the positioning sentence. Topics
      (GitHub allows 20; these are the ones people browse):
      `mir`, `mobile-industrial-robots`, `amr`, `agv`, `vda5050`,
      `robotics`, `emulator`, `simulator`, `rest-api`, `openapi`, `mqtt`,
      `mcp`, `mcp-server`, `massrobotics`, `omron`, `fleet-management`,
      `industrial-automation`, `testing`, `python`. (`github.com/topics/vda5050`
      and `/topics/mobile-industrial-robots` both exist.) Acceptance:
      `gh repo view --json repositoryTopics,description` shows them.
- [ ] **Cut a release.** No tags exist. A `v*` tag triggers `release.yml`,
      gives the repo a "Latest release", and gives posts something to link.
      Acceptance: `gh release list` is non-empty with notes generated from
      the tracked-version table.
- [ ] **Make the site crawlable.** Serve `/robots.txt` and `/sitemap.xml`
      from `serverless.py` (page list comes from `SITE_PAGES`), add
      canonical + Open Graph tags and `SoftwareApplication` JSON-LD to the
      pages, and serve HTML to browsers at `/` (content-negotiate; API
      clients and the discovery handshake keep the JSON index). Add
      `/llms.txt` pointing at the endpoints and the auth recipe — agents
      are a real audience here. Acceptance: all three URLs return 200 with
      the right content type; `curl -H 'Accept: text/html'
      https://amr-emulator.com/` returns the landing page;
      the JSON index that `mir_client.detect_server()` probes is unchanged
      for clients that do not ask for HTML (regression test in
      `test_serverless.py`).
- [ ] **README above the fold.** Today the README opens on VDA 5050 and
      reaches a MiR `curl` after two sections; the MiR visitor — the stated
      audience — should see "hosted URL, one curl, one `pip install`" in
      the first screen, with the monorepo detail below. Acceptance: a
      reader who knows only "MiR REST API" can copy one command from the
      first screen and get a status document.
- [ ] **Turn on GitHub Discussions** (or decide not to). Issues here are
      written for agents (`REQUESTS.md`); "how do I…" from an integrator
      needs somewhere lower-friction. Acceptance: decision recorded here.

## Phase 1 — time to first request

Target: someone who lands on any entry point gets a real status document
back in **under 60 seconds without installing anything**, and under 5
minutes locally.

- [ ] **Zero-install path is the default.** The console at
      `amr-emulator.com/console` already gives a private virtual robot;
      the page simplification in flight (`feat/mir-page-simplify`) is the
      right direction — first request directly under the intro. Acceptance:
      from page load to a 200 `GET /status` is one click; measured by the
      endpoint log, median time from first page hit to first API 200 per
      session.
- [ ] **The auth recipe, in every language the console already shows**
      (cURL/Python/JavaScript/Go/Rust), as its own linkable section. This
      is the search-traffic page. Acceptance: a standalone URL whose title
      contains "MiR REST API authorization" and whose first code block
      works verbatim against both the hosted emulator and (per
      `TEST_HARDWARE.md` phase 5) a real robot.
- [ ] **"Switch to your robot" step.** The promise is "same code, real
      robot". Show the one-line change (base URL + credentials) and what
      to expect to differ (no `/_emulator/*`, no `X-MiR-Session`).
      Acceptance: the quickstart ends with that diff, and it has been
      exercised on hardware.
- [ ] **CI recipe.** A copy-paste block for GitHub Actions (`services:`
      container) and for `pytest` (`create_app("3.8.1")` under
      `TestClient`, already supported). Acceptance: a public example repo
      or `examples/` directory whose CI is green using only published
      artifacts.
- [ ] **MCP in one line.** After PyPI: `claude mcp add mir -- uvx mir-mcp`
      with `MIR_ROBOT_URL` defaulting to something that works. Then list
      it. Acceptance: listed in the official MCP registry
      (`registry.modelcontextprotocol.io`) and a PR open against
      `punkpeye/awesome-mcp-servers`.

## Phase 2 — content that earns the click

Each piece answers a question someone is already asking, shows a result
first, and ends on the hosted URL. One per week, not a burst.

1. **"MiR REST API authorization: why `curl -u` returns 401."** The
   SHA-256 detail, the five-language recipe, a robot to try it on. Highest
   search intent of anything we can write.
2. **"What changed in the MiR REST API between 2.x and 3.x."** Generated
   from `/_emulator/diff?from=2.14.7&to=3.8.1` — nobody else has this
   data in machine-readable form. Useful to every site doing a software
   upgrade.
3. **"Testing a MiR integration in CI without a robot."** The container +
   fault-injection story: e-stop mid-mission, blocked path, latency.
4. **"We converted MiR's API PDFs back into Swagger."** The engineering
   story (`pdf_convert.py`, the 3.5.4 oracle). This is the Hacker News /
   developer-audience piece; it is interesting independent of MiR.
5. **"Driving a MiR from a VDA 5050 master control."** The adapter and the
   Isaac Mission Dispatch run (`docs/validation/mir-adapter-mission-dispatch.md`).
6. **"A VDA 5050 robot fleet with zero infrastructure."** Embedded broker,
   three protocol versions, the schema defects found along the way.
7. **Scenario write-ups.** `scenarios/` already reconstructs nine
   deployments; two or three become short posts with the `mir-report`
   output as the picture.
8. **A 90-second screen recording** of the console: get a robot, queue a
   mission, hit the e-stop, clear it. Embedded on the page and the README.
9. **After hardware testing:** "We ran the emulator against a real
   MiR<model>: what matched, what didn't." The single most credible piece
   available to us; it is why `TEST_HARDWARE.md` is a promotion
   dependency.

Home for these: the site itself (same domain, so the search value
accrues to `amr-emulator.com`), cross-posted where relevant.

## Phase 3 — channels

Only places confirmed to exist (HTTP 200 on 2026-10-01 unless noted), and
what fits each. One post per channel, written for that channel; answer
existing questions before posting anything of our own.

| Channel | Audience | What to post | Notes |
|---|---|---|---|
| Open Robotics Discourse (`discourse.openrobotics.org`) | ROS / Open-RMF developers | Piece 5 or 6; the adapter and VDA 5050 emulator | `DFKI-NI/mir_robot` (the ROS driver for MiR) lives in this world; its users are the nearest existing MiR developer community on GitHub |
| Robotics Stack Exchange (`robotics.stackexchange.com`) | Q&A | Answer MiR REST / VDA 5050 questions; link only where it is the answer | No announcements here |
| VDA5050 GitHub (`github.com/VDA5050/VDA5050`, Issues + Discussions) | Standard maintainers and implementers | The schema-defect issues already queued in `TODO.md`; a Discussions post offering the emulator as a test target | Contribution first |
| `inorbit-ai/ros_amr_interop` | Connector maintainers | The three drafted issues in `interop/otto-vda5050/UPSTREAM_ISSUES.md` | Already an open `TODO.md` item |
| `nvidia-isaac/isaac_mission_dispatch` | Mission Dispatch users | A short "tested against" note with the reproduce steps from `docs/validation/` | |
| `MassRobotics-AMR/AMR_Interop_Standard` | Interop WG | The emulator + receiver validation in `interop/massrobotics/` | |
| Inductive Automation forum (`forum.inductiveautomation.com`) | Ignition integrators — real MiR REST threads exist | Answer the existing MiR threads with the auth recipe and a test endpoint | Highest density of the "integrator" audience found |
| Universal Robots forum (`forum.universal-robots.com`) | UR+MiR cell builders — MiR threads exist | Same: answer, don't announce | |
| Robot-Forum (`robot-forum.com`) | Industrial robot practitioners — a MiR thread exists | Same | |
| Hacker News, Show HN | Developers at large | Piece 4, title leading with the PDF→Swagger angle | One shot; do it after Phase 0 so the top comment is not "how do I install it" |
| Reddit r/robotics, r/ROS, r/PLC | Mixed | Piece 3 (r/PLC), 5/6 (r/ROS) | **Existence not machine-verified** (Reddit answers 403 to scripted requests); each has self-promotion rules — read them first |
| Awesome lists: `punkpeye/awesome-mcp-servers`, `kiloreux/awesome-robotics` | Browsers of lists | One-line PRs | After PyPI/registry |
| MCP registry (`modelcontextprotocol/registry`) | Agent developers | `mir-mcp` entry | Needs the PyPI package |
| LinkedIn | Automation managers, MiR distributors, MiR staff | The recording + piece 9 | Where the non-developer half of the MiR audience actually is; no API to verify anything here |
| MiR Community (`mobile-industrial-robots.com/community`) | MiR partners and customers | — | Described as closed to partners/customers. Only relevant if Nick has access; see open questions |
| MiR directly | API / partner engineering | `FEEDBACK.md` as a private, constructive note, plus an offer: a test target their integrators can use | Before any public post that mentions the feedback. A MiR Academy "Software Integration" path exists (`academy.mobile-industrial-robots.com`) — a link from there would outrank everything above |
| MiR distributors / integrators | People who train customers on the API | Direct email with the recording; a distributor ran a public "MiR REST API Python scripting" webinar (Robotics Plus), i.e. this audience teaches the thing we emulate | A handful of personal emails, not a campaign |

## Phase 4 — upstream contributions as promotion

The most durable visibility is being the project that found and reported
the bugs. All of this is already drafted in the repo.

- [ ] **File the OTTO connector issues** (`TODO.md` → "File the OTTO
      connector bugs"). Acceptance as stated there; additionally each
      issue's reproduce section uses a published artifact, not a checkout.
- [ ] **File the VDA 5050 schema defects** (`TODO.md` → "File the upstream
      schema defects"). Same.
- [ ] **Send `FEEDBACK.md` to MiR.** Acceptance: sent to a named contact,
      date recorded here; any reply summarized in `FEEDBACK.md`.
- [ ] **Offer the converted specs back.** The top ask in `FEEDBACK.md` §3.1
      is machine-readable specs; we have them. Whether we may publish them
      as a standalone artifact is the licensing question below.
- [ ] **"Works with" backlinks.** Where a harness validates someone's
      project (`ros_amr_interop`, Mission Dispatch, the MassRobotics
      reference receiver), ask for a line in their docs.

## Metrics

Count things that indicate use, not attention. Baseline is zero for all of
them today; record the first reading the week Phase 0 lands.

| Metric | Source | Why |
|---|---|---|
| Distinct sessions making ≥1 authenticated API call on the hosted demo, per week | endpoint logs (the amr-emulator log-triage routine already reads them) | The real number: someone used it |
| Sessions that go past `GET /status` (queue a mission, inject a fault) | same | Depth, not a drive-by |
| Median page-load → first 200 | same | Time-to-first-request target (< 60 s) |
| PyPI downloads per package, per week | PyPI stats | Local/CI adoption |
| Container pulls | GHCR | CI adoption |
| Inbound issues/discussions from non-maintainers | GitHub | Somebody cared enough to write |
| Hardware-observed discrepancy reports | issues using the `REQUESTS.md` template with "observed on a real robot" as source | The audience we most want |
| Stars, forks, referrers, search queries | GitHub traffic (14-day window — record weekly), Search Console once the domain is verified | Trailing indicators only |

Privacy: log-derived metrics are counts. No IPs, session ids, or request
bodies leave the log store or get committed.

Six-week bar after Phase 0: 25 distinct weekly sessions past `GET
/status`, 3 non-maintainer issues or discussions, 1 inbound report from
someone with a physical robot. Miss it and the conclusion is that
positioning or channels are wrong — revisit this file, do not post more.

## Sequence

1. Phase 0 in the order listed (PyPI names first — it is the only item with
   an external race).
2. Finish the console simplification; record the 90-second video against
   the new page.
3. Run `TEST_HARDWARE.md`. Rewrite the fidelity claims with what it finds.
4. File upstream issues (Phase 4) — they are ready and cost nothing.
5. Publish piece 1 and answer the existing forum threads with it.
6. One piece per week through piece 6; Show HN with piece 4.
7. Week 6: read the metrics against the bar.

## Open questions for Nick

- **Spec redistribution.** The robot API files come from MiR's support
  portal behind a free login; the repo and the hosted demo redistribute
  converted copies. Has that been cleared, or is it worth asking MiR
  before the project gets visible? It decides whether "offer the specs
  back" is a gift or an admission.
- **PyPI ownership.** Personal account or an `advin` organization? It
  decides the trusted-publisher configuration and cannot be changed
  casually later.
- **Do you have MiR Community / distributor access?** The best channels
  (MiR Community, MiR Academy, partner engineering) are closed; a warm
  contact is worth more than everything in Phase 3.
- **Is the non-affiliation disclaimer on every public page already?** Not
  audited here (the site pages were out of scope for this document).
- **Naming.** The repo is `amr-emulator`, the flagship package
  `mir-emulator`, `CONTRIBUTING.md` still says `cd mir-emulator`, and the
  MCP README says `/path/to/mir-emulator`. Pick the name the MiR audience
  should remember before it is printed in posts.
- **Is "free hosted endpoint" a commitment?** Promotion means load on a
  Lambda you pay for; say what the limit is (rate, session cap) before
  inviting the internet.
