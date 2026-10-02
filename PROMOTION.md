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
| PyPI | **nothing published, and nothing will be** — decided 2026-10-01: this is a web endpoint, not a library. All nine package names answer 404 | `curl https://pypi.org/pypi/<name>/json` |
| `pip install` / `uvx` claims | were stated in `README.md`, `docs/landing.html` and `packages/mir-emulator/README.md`; removed 2026-10-01 in favour of "from a checkout" | `grep -n "pip install\|uvx"` |
| Container image | **not published anywhere.** `ci.yml` builds `mir-emulator:ci` and smoke-tests it; no workflow pushes to a registry | `grep -i "ghcr\|docker" .github/workflows/*.yml` |
| Hosted demo | up. `https://amr-emulator.com/` → 200 JSON index, `/console` → 200 HTML, `/healthz` lists 9 robot + 3 fleet versions, `/latest/api/v2.0.0/status` → 401 without auth (correct) | `curl` |
| Crawlability | `/robots.txt`, `/sitemap.xml`, `/llms.txt` all 404 (as JSON); the bare domain serves JSON, not a page | `curl` |
| Page metadata | `docs/index.html`, `landing.html`, `vda5050.html` have `<title>` and `<meta name="description">`; no Open Graph, canonical, or JSON-LD tags found | `grep` over `docs/*.html` |
| MCP registry | `mir-mcp` not listed (search for "mir" returns unrelated servers only). With no published package, a listing would have to point at a hosted MCP endpoint instead | `curl "https://registry.modelcontextprotocol.io/v0/servers?search=mir"` |
| GHCR listing | **unverified** — the `gh` token lacks `read:packages`; the workflow evidence above says nothing is pushed | `gh api users/JimothyJohn/packages` → 403 |
| Search ranking, inbound links, traffic | **unverified** — nothing measured yet (see Metrics) | — |

Short version: the product is the hosted endpoint, it is live, and the
work is real — but nothing tells a search engine or a registry that it
exists. Every post ends on `https://amr-emulator.com`, never on an install
command; the checkout is for people who want to run it offline or
contribute. Fix findability before posting anywhere.

## Who is looking, and what they type

| Audience | Their problem | What they search for | What we hand them |
|---|---|---|---|
| **Integrator / automation engineer** with a MiR on order or on a busy floor (PLC, SCADA, MES/WMS people; Ignition, UR+MiR cells) | Cannot develop against a robot that is not there or is in production | "MiR REST API example", "MiR REST API authorization", "MiR API 401", "MiR mission queue POST", "MiR robot simulator" | Hosted URL that answers the same requests + the auth one-liner |
| **Software developer** building a WCS/dashboard/app on MiR or MiR Fleet | No test target for CI; version drift between robots | "MiR API mock", "MiR Fleet API sandbox", "MiR python client", "MiR openapi / swagger json" | The hosted URL as the CI target (one `X-MiR-Session` per run), `/openapi.json` to generate their own client |
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

The name is **AMR Emulator** — `amr-emulator` where spaces cannot be used
(repo, domain, paths). Never "mir-emulator" as the project's name; that
string survives only as an internal Python package name.

One sentence, reused everywhere (repo description, page title, post
titles):

> **AMR Emulator: a MiR robot REST API you can develop against without a
> robot** — spec-faithful, every tracked software version, one free public
> URL.

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
published API definitions"; after it, "validated against a MiR250
running <version>" becomes the strongest line we have.

### Affiliation and trademark

"MiR" and "Mobile Industrial Robots" are MiR's marks. Required everywhere
we publish:

- A visible non-affiliation line in the footer of every site page (added
  2026-10-01 to all seven pages under `docs/`). The README and package
  READMEs do not carry one yet.
- Use the name descriptively ("emulator of the MiR REST API"), never as our
  brand. No MiR logo, no MiR colours or product photos.
- The specs are redistributed from MiR's support portal, whose robot API
  files sit behind a (free) login. MiR is fine with this and welcomes a
  free emulator (per Nick, 2026-10-01); nothing in writing is recorded in
  this repo.
- `scenarios/` cite published MiR customer case studies by company name.
  Keep them framed as "reconstructed from the public case study", linked,
  with no implication those companies use this project.
- `FEEDBACK.md` is critical of MiR's API. Keep it factual and
  version-specific (it is); never lead a post with it.

## Phase 0 — make it findable

Nothing in Phase 1+ starts until these are done. Ordered.

- [ ] **Billing alarm on the hosted endpoint.** No rate or session limit
      is planned; the AWS bill is the tripwire. Before inviting traffic,
      confirm an alarm exists on the account's estimated charges and that
      the Lambda has a concurrency ceiling. Acceptance: `aws cloudwatch
      describe-alarms` shows the billing alarm; the function's reserved
      concurrency is set.
- [ ] **Repo metadata.** Description → the positioning sentence. Topics
      (GitHub allows 20; these are the ones people browse):
      `mir`, `mobile-industrial-robots`, `amr`, `agv`, `vda5050`,
      `robotics`, `emulator`, `simulator`, `rest-api`, `openapi`, `mqtt`,
      `mcp`, `mcp-server`, `massrobotics`, `omron`, `fleet-management`,
      `industrial-automation`, `testing`, `python`. (`github.com/topics/vda5050`
      and `/topics/mobile-industrial-robots` both exist.) Acceptance:
      `gh repo view --json repositoryTopics,description` shows them.
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
      audience — should see "hosted URL, one curl" in
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
      `amr-emulator.com/console` already gives a private virtual robot,
      and since the page simplification (PR #106) the first request sits
      directly under the intro. Acceptance:
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
- [ ] **CI recipe.** A copy-paste block for GitHub Actions that points a
      test suite at the hosted endpoint with a fresh `X-MiR-Session` per
      run, so parallel jobs never share a robot. Acceptance: a public
      example repo or `examples/` directory whose CI is green against
      `https://amr-emulator.com` with nothing installed from this repo.
- [ ] **MCP as an endpoint, not a package.** Today `mir-mcp` runs from a
      checkout over stdio (`packages/mir-mcp/README.md`). The
      web-endpoint-shaped version is a hosted MCP URL; the unmerged local
      branch `feat/mcp-serverless` adds a streamable-HTTP transport and a
      deploy template for exactly that (the template is an unreviewed wip
      snapshot). Whether the official registry lists remote-only servers
      was not checked. Acceptance: `claude mcp add --transport http` against
      a public URL drives the hosted emulator, then a registry entry and a
      PR against `punkpeye/awesome-mcp-servers`.

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
   MiR250: what matched, what didn't." The single most credible piece
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
| Hacker News, Show HN | Developers at large | Piece 4, title leading with the PDF→Swagger angle | One shot; do it after Phase 0 |
| Reddit r/robotics, r/ROS, r/PLC | Mixed | Piece 3 (r/PLC), 5/6 (r/ROS) | **Existence not machine-verified** (Reddit answers 403 to scripted requests); each has self-promotion rules — read them first |
| Awesome lists: `punkpeye/awesome-mcp-servers`, `kiloreux/awesome-robotics` | Browsers of lists | One-line PRs | After the hosted MCP endpoint exists |
| MCP registry (`modelcontextprotocol/registry`) | Agent developers | `mir-mcp` entry | Needs the hosted MCP endpoint (Phase 1) |
| LinkedIn | Automation managers, MiR distributors, MiR staff | The recording + piece 9 | Where the non-developer half of the MiR audience actually is; no API to verify anything here |
| MiR Community (`mobile-industrial-robots.com/community`) | MiR partners and customers | Piece 1, then the recording; answer API questions with the hosted URL | Closed to partners/customers; **Nick has access.** With Academy and distributor contacts this is the first channel, ahead of every public one above |
| MiR directly | API / partner engineering | `FEEDBACK.md` as a private, constructive note, plus an offer: a test target their integrators can use | Before any public post that mentions the feedback. MiR already welcomes the project and Nick has Academy access; a MiR Academy "Software Integration" path exists (`academy.mobile-industrial-robots.com`) — ask for a link from it, which would outrank everything above |
| MiR distributors / integrators | People who train customers on the API | Direct email with the recording; a distributor ran a public "MiR REST API Python scripting" webinar (Robotics Plus), i.e. this audience teaches the thing we emulate | A handful of personal emails, not a campaign |

## Phase 4 — upstream contributions as promotion

The most durable visibility is being the project that found and reported
the bugs. All of this is already drafted in the repo.

- [ ] **File the OTTO connector issues** (`TODO.md` → "File the OTTO
      connector bugs"). Acceptance as stated there; additionally each
      issue's reproduce section pins a commit of this repo.
- [ ] **File the VDA 5050 schema defects** (`TODO.md` → "File the upstream
      schema defects"). Same.
- [ ] **Send `FEEDBACK.md` to MiR.** Acceptance: sent to a named contact,
      date recorded here; any reply summarized in `FEEDBACK.md`.
- [ ] **Offer the converted specs back.** The top ask in `FEEDBACK.md` §3.1
      is machine-readable specs; we have them, and MiR is fine with the
      project redistributing them. Acceptance: offered to the same named
      contact as `FEEDBACK.md`.
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
| AWS cost of the hosted endpoint, per week | Cost Explorer / the billing alarm | The only limit on "free": no rate or session cap is planned unless the bill spikes |
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

1. Phase 0 in the order listed.
2. Record the 90-second video against the simplified console page.
   Start the MiR Community / Academy conversations now — they do not wait
   on anything.
3. Run `TEST_HARDWARE.md`. Rewrite the fidelity claims with what it finds.
4. File upstream issues (Phase 4) — they are ready and cost nothing.
5. Publish piece 1 and answer the existing forum threads with it.
6. One piece per week through piece 6; Show HN with piece 4.
7. Week 6: read the metrics against the bar.

## Decisions (Nick, 2026-10-01)

- **Spec redistribution:** MiR is fine with it and welcomes a free
  emulator.
- **No PyPI.** This is a web endpoint, not a library. Local use is from a
  checkout. `release.yml` still builds wheels as workflow artifacts and
  carries a dormant publish step.
- **Closed channels:** Nick has MiR Community, Academy and distributor
  access; those lead Phase 3.
- **Disclaimer:** in the footer of every site page.
- **Name:** AMR Emulator, or `amr-emulator` where spaces cannot be used.
- **Hosted endpoint limits:** none planned unless the AWS bill spikes.
- **Hardware target:** a MiR250 (`TEST_HARDWARE.md`).

## Open questions for Nick

- **Container image.** With PyPI ruled out, is a published container also
  out? It was dropped from Phase 0 on that reading; the `Dockerfile` stays
  for CI and self-hosting from a checkout.
- **`release.yml` publish step.** Remove the dormant PyPI step, or leave
  it? It is a deploy-chain edit, so it was not touched here.
- **Package names.** The Python packages are still `mir-emulator`,
  `mir-client`, `mir-mcp`. Renaming them is a refactor across imports,
  CLIs and CI; say if "everything" includes them.
