# API feedback for the MiR development team

This document collects concrete, version-specific issues we found while building
[mir-emulator](README.md), a spec-faithful emulator of the MiR robot REST API and the
MiR Fleet Enterprise Integration API. Every finding below was observed either in the
official API definitions themselves or in behavior we had to special-case to stay
faithful to real robots. We track the latest patch of the newest four minor lines of
each major release, and once a minor line is tracked it stays tracked permanently
(updated to its latest patch, never dropped). Currently:

- **Robot REST API** (`/api/v2.0.0`): 2.10.5.8, 2.12.0.4, 2.13.5.4, 2.14.7, 3.5.4, 3.5.6, 3.6.7, 3.7.2, 3.8.1
- **Fleet Enterprise Integration API** (`/api/v1`): 1.3.1, 1.4.2, 1.5.0

**Provenance caveat:** MiR has published exactly one machine-readable robot spec ever
(the 3.5.4 `swagger.json`). All other robot-side findings come from our PDF→Swagger
conversion, which is validated for zero structural drift against that 3.5.4 document
on every run. Findings that could conceivably be conversion artifacts are flagged;
naming, auth, enum, and type-format findings are inherent to the published definitions.
Fleet findings come from your own OpenAPI 3 JSON documents, used verbatim.

---

## 1. Robot REST API

### 1.1 Breaking changes ship without aliases or deprecation notices

- **`area_events` was renamed wholesale to `zones` at the 2.x → 3.x boundary**
  (last seen in 2.14.7, gone in 3.5.4). Seven paths removed (`/area_events`,
  `/area_events/{guid}`, `/area_events/definitions`,
  `/area_events/action_definitions[/{action_type}]`, `/maps/{map_id}/area_events`)
  and recreated under `/zones/...`, with definitions renamed in lockstep
  (`GetArea_event` → `GetZone`, `PostArea_events` → `PostZones`, `PutArea_event` → `PutZone`).
  It is a pure rename with no compatibility alias, so every 2.x integration touching
  zones breaks on upgrade. A transition period where both paths respond (one marked
  deprecated) would have made this a non-event.
- **Whole feature areas were deleted at 2.14.7 → 3.5.4 with no replacement or notice
  in the API definition:** all Bluetooth endpoints (`/bluetooth`, `/bluetooth/scan`,
  `/bluetooth_relays[/{guid}]`) and most elevator control (`/elevator_status[/{guid}]`,
  `/elevators/{guid}/cmd_check_server`, `/cmd_control`, `/cmd_door`, `/cmd_floor`,
  `/opcua_scanner`). A changelog section in the API docs listing removals per release
  would let integrators audit upgrades instead of discovering 404s in production.
- **Endpoint churn:** `/wifi/certificates`, `/wifi/certificates/{file_name}`, and
  `/wifi/experimental` appear in 2.13.5.4, survive 2.14.7, and vanish in 3.5.4 —
  a surface that existed for roughly one minor line.
- **Silent type change:** `GetSetting.constraints` and `GetSetting_advanced.constraints`
  changed from `string` to `object` between 2.14.7 and 3.5.4. This is the only
  definition-property type change we found across all consecutive tracked versions,
  and nothing in the documentation calls it out.

### 1.2 The `basePath` version is frozen and misleading

Every tracked release from 2.10.5.8 through 3.8.1 serves `/api/v2.0.0`, while
`info.version` tracks the real product release. The path segment suggests API
versioning that does not exist: the surface changes materially between releases
(145 paths in 2.10–2.12, 150 in 2.13–2.14, 157 in 3.5–3.7, 159 in 3.8.1) but the
path version never moves. Either version the path meaningfully or drop the
pseudo-version; the current scheme gives integrators false confidence that
`v2.0.0` code is portable across robots.

### 1.3 Spec correctness errors (all tracked versions unless noted)

- **`type: integer` combined with `format: float` on 47–53 properties per version.**
  Examples: `PostElevators.port`, `PostMission_actions.priority`,
  `PostIo_modules.num_inputs` / `num_outputs`, `PutHook_height.height`,
  `PostWifi_connection.bgscan_threshold`. These are contradictory declarations —
  a port or a count is not a float — and they break strict code generators.
- **Collection GET endpoints declare the element schema instead of an array.**
  E.g. `GET /actions` is typed as the single `GetAction_definitions` object, yet
  real robots return a JSON array. The singular/plural definition pairs are
  byte-identical (`GetError_report` ≡ `GetError_reports`,
  `GetAction_definition` ≡ `GetAction_definitions`,
  `GetPosition_transition_list` ≡ `GetPosition_transition_lists`,
  `GetPaths` ≡ `GetMap_paths`). Our emulator carries a dedicated workaround
  (`_item_schema_for` in `app.py`) purely to reconcile the spec with observed
  robot behavior.
- **The same field is typed differently between request and response for one
  resource:** `Mission_action.parameters` is `string` on GET but `array` on PUT;
  same for `Mission_actions.parameters` (GET/POST), `Modbus_mission.parameters`
  (GET/PUT), and `Zone.actions` (object on GET, array on PUT). Clients cannot
  round-trip a GET body back into a PUT without undocumented transformations.
- **23 response schemas in 3.8.1 are completely empty** (`{"type":"object","properties":{}}`),
  including user-facing endpoints: `GET /system/info`, `GET /metrics`,
  `GET /world_model`, `GET /wifi`, `GET /robots`, `GET /experimental/diagnostics`,
  `GET /system/protective_scan`, `GET /platform/timezone`. The response body is
  entirely unspecified for these.
- **Zero of 1,307 definition properties use JSON-Schema `enum`** (3.8.1). Every
  constrained field encodes its allowed values in prose instead — e.g.
  `PutStatus.state_id` is documented only as the description text
  `"Choices are: {3, 4, 11}, State: {Ready, Pause, Manualcontrol}"`. Machine
  consumers cannot validate or generate typed bindings from prose.
- **Read-side `state_id` values are not enumerated anywhere in the API definition.**
  `GetStatus.state_id` is a bare integer. We had to pin the value set from the
  `mir_msgs/RobotState.msg` ROS table (e.g. `EMERGENCYSTOP=10`, `ERROR=12`) —
  an internal source integrators should not need.
- **Only 44 of 249 definitions declare a `required` array** (3.8.1). Most request
  bodies never state which fields are mandatory, so integrators discover
  requiredness by trial and error against hardware.

### 1.4 Naming inconsistencies

- The same identifier gets three different path-parameter names on sibling paths:
  `/mission_groups/{guid}` vs `/mission_groups/{group_id}/missions` vs
  `/mission_groups/{mission_group_id}/actions`. Positions likewise:
  `/positions/{guid}`, `/positions/{pos_id}/docking_offsets`,
  `/positions/{parent_guid}/helper_positions`.
- Three id-parameter conventions coexist across the API: `{guid}` (39 paths),
  `{id}` (12 paths), and the lone `{uuid}` on `/wifi/connections/{uuid}`.
- Definition names mix PascalCase verb prefixes with snake_case suffixes
  (`GetAction_definition`, `PutCart_calibration`, `PostIo_module_status`) —
  248 of 249 names in 3.8.1 have no consistent convention, which produces ugly
  generated-client identifiers in every language.
- 35 groups of structurally identical definitions exist in 3.8.1 (including a
  23-member group of empty objects) instead of shared `$ref` reuse.

### 1.5 Authentication is non-standard and under-documented

- The API requires `Authorization: Basic BASE64(<username>:SHA-256(<password>))` —
  the password is SHA-256-hex-digested before the colon join. No off-the-shelf
  HTTP Basic client does this, yet the security definition is declared as plain
  `{"type": "basic"}` (RFC 7617), which is actively misleading: `curl -u`,
  requests' `HTTPBasicAuth`, and every generated client fail out of the box.
- **The SHA-256 scheme is documented in only 1 of 9 tracked specs** (3.5.4 carries
  a description; 2.10.5.8 through 3.8.1 otherwise ship a bare `{"type":"basic"}`).
  The single most surprising integration step is undocumented in eight of nine
  published definitions.
- **No operation declares a `security` requirement** in any version — auth is
  defined but never attached to endpoints, so tooling cannot tell which routes
  are protected (in practice: all of them).
- `schemes` is `["http"]` only. If TLS is supported, the definitions should say so.

---

## 2. Fleet Enterprise Integration API (1.3.1, 1.4.2, 1.5.0)

First, credit where due: publishing native OpenAPI 3 JSON at stable public URLs, with
no login wall, is exactly right — see §3. The issues below are about the contents.

### 2.1 Colliding schema names with numeric `-1` suffixes — and the debt is growing

The specs contain machine-generated name collisions: 16 `-1`-suffixed schemas in
1.3.1, 18 in 1.4.2, 19 in 1.5.0 (`position-1`, `pose-1`, `charger-1`, `map-1`,
`zone-1`, `error-1`, ...). These are almost certainly artifacts of your spec
generator flattening two C# namespaces into one schema pool. Consequences:

- **Same name, unrelated meaning:** `marker-type` is an object
  (`name`, `docking-type`, `offset`, ...) while `marker-type-1` is an enum
  (`['V','VL','L','Bar','PalletRack','Stripe']`). Nothing but the suffix
  distinguishes them.
- **`footprint` vs `footprint-1`** are two unrelated footprint concepts
  (`{points, height}` vs `{name, robot-types, has-hook, height, points}`).
- **`order-status` and `order-status-1` are byte-identical enums** — `order-status-1`
  is pure accidental duplication newly introduced in 1.5.0.
- Generated clients inherit the noise: our Python client ends up with
  `Position1`, `UtilityPosition1`, etc., and no way to name them better.

### 2.2 Request and response models for the same resource diverge

`POST /api/v1/site/position` accepts the `position` family, where the discriminator
is named `base-position-type` and poses use `pose`. `GET /api/v1/site/position/{id}`
returns the `position-1` family, where the discriminator is named just `type`, poses
use `pose-1`, and extra fields appear (`load-jam-detection-enabled`,
`entry-positions`). Related: `entry-position` requires `offset-pose` while
`entry-position-1` makes it optional. Round-tripping a GET into a POST requires
field renames — read and write models for one resource should share schemas or at
least field names.

### 2.3 Three documents, three conventions

- **Property casing:** the Integration and Top-Module APIs use kebab-case JSON
  properties (`map-id`, `total-distance-moved-in-meters`); the Compatibility API
  uses snake_case (`session_id`, `mission_group_id`). One product, two casings.
- **The lone snake_case property inside the Integration API,**
  `subscription-type-response.event_types`, is also marked `deprecated: true`
  with no documented replacement.
- **Path parameters are camelCase (`{serialOrderId}`, `{mapId}`) inside kebab-case
  and snake_case path segments** — three casings can appear in a single URL.
- **Error models:** the Integration API defines three overlapping error schemas
  (`problem-details` per RFC 9457, `error`, and `error-1`); the Compatibility API
  mixes `error-response`, `problem-details`, and untyped bodies (all 39 of its 5xx
  responses declare no schema); the Top-Module API defines no error shape at all.
  Standardizing on `problem-details` everywhere would fix this in one move.

### 2.4 Machine-consumption gaps

- **112 of 112 operations in 1.5.0 have no `operationId`** (same in 1.3.1/1.4.2).
  Every generated client falls back to path-derived names like
  `post_api_v1_site_position`.
- **No document declares a `servers` array**, so clients cannot programmatically
  distinguish the `/api/v1` root from the Compatibility API's
  `/compatibility_api/v1` root.
- **The `id` path parameter changes type by endpoint:** `string`/`uuid` on most
  operations, format-less `string` on `GET /api/v1/serial-order/{id}`,
  `DELETE /api/v1/site/map/{id}`, `DELETE /api/v1/site/position/{id}`, and
  `integer`/`int32` on `GET /compatibility_api/v1/evacuations/{id}`.
- **Resource modeling is split inconsistently:** orders read from `/api/v1/order`
  but write through `/api/v1/serial-order`, whose own parameter is `{id}` on
  GET/DELETE but `{serialOrderId}` on the fallback route. Singular and plural
  nouns coexist (`/api/v1/site/position` vs `/compatibility_api/v1/positions`).

### 2.5 Two products, two unrelated auth schemes

Fleet uses an `x-api-key` header; the robots use the non-standard hashed-Basic
scheme from §1.5. An integrator working across both (a common scenario — Fleet plus
direct robot access for diagnostics) must implement two entirely different auth
stacks for one vendor. Converging on one scheme — ideally standard bearer/API-key
auth on both — would simplify every integration.

On the positive side: the fleet versions we track have been strictly additive
(no path or schema removed 1.3.1 → 1.4.2 → 1.5.0). Please keep that property.

---

## 3. Documentation & publishing

This is our highest-impact ask.

### 3.1 Publish the robot API as machine-readable specs, not PDFs

The robot REST API definitions are published only as PDFs — swagger2markup +
Asciidoctor renderings of what is clearly an internal Swagger document. To emulate
the API we had to build a ~400-line converter that reverses that rendering, plus a
correctness oracle and ~600 lines of tests, and it must compensate for problems that
exist only because of the format:

- Identifiers wrap mid-word across table-cell lines (`PostCart_calibratio\nns`),
  and `required`/`optional` flags are glued into the name cell.
- Type information that was machine-readable at the source
  (`< GetMissions > array`, `< string,object > map`, `enum(en_US,de_DE)`,
  `string(date-time)`) must be re-parsed from rendered strings with hand-built
  heuristics.
- Some information is destroyed outright: `< object > array` is ambiguous between
  a typed-items array and an itemless one; the distinction existed in your source
  Swagger and cannot be recovered from the PDF.
- Tables break across pages with repeated header rows; inline nested objects are
  exploded into separate headings that must be folded back; the same sub-schema
  name can appear twice with different shapes.

**You already have the source documents** — the PDFs are generated from them, and
you published one directly once (3.5.4 `swagger.json`). Publishing that JSON next
to each PDF would cost nothing and would eliminate this entire class of tooling for
every integrator, not just us. The Fleet side proves the model works: native
OpenAPI 3 JSON at public URLs, consumable verbatim. Our fleet sync is a ~240-line
HTTP fetch; our robot sync is ~650 lines of PDF/login/oracle machinery guarded by
~600 lines of tests.

### 3.2 Portal friction

- Robot API docs sit behind a login wall (the Fleet specs correctly do not).
  API reference material should be public.
- File naming is inconsistent across versions and products in one listing
  (`mir_rest_api_3.5.4.json`, `mir_rest_api_2.14.7.zip`,
  `mir_mir250_rest_api_2.13.3.1.yaml`), some files ship zipped and some not, and
  the PDF's self-reported version occasionally disagrees with its filename.
- Version numbers mix three- and four-part forms (3.8.1 vs 2.13.5.4, 2.12.0.4,
  2.10.5.8), which breaks naive semver handling in any tooling.
- ~500 near-identical per-product PDFs per listing (MIR100/200/250/500/600/1000/1350)
  force consumers to guess which one is canonical. If the API is identical across
  platforms, one document per version — or a machine-readable index — would say so.

### 3.3 A changelog per release

None of the changes in §1.1 (renames, removals, type changes) is announced in the
API definitions themselves. A per-release "added / removed / changed" section —
which you could generate mechanically from the same source Swagger — would turn
upgrade audits from spelunking into a diff read.

---

## Summary of asks, in priority order

1. **Publish the robot API definition as `swagger.json`/OpenAPI alongside (or instead
   of) the PDF, for every release** — you did it once for 3.5.4; the Fleet pipeline
   shows it works. (§3.1)
2. **Document the non-standard Basic-auth SHA-256 scheme in every spec version and
   attach `security` requirements to operations.** (§1.5)
3. **Fix spec-vs-robot mismatches:** array responses typed as objects,
   request/response type flips, `integer`+`float` contradictions, empty response
   schemas. (§1.3)
4. **Use `enum` and `required` in schemas instead of prose descriptions.** (§1.3)
5. **Fleet: fix the `-1` schema-name collisions before the count grows further, add
   `operationId`s and `servers`, unify request/response models and error shapes.** (§2)
6. **Ship a machine-generated changelog per release; alias renamed endpoints for one
   deprecation cycle.** (§1.1, §3.3)
7. **Make robot API docs public and normalize portal file naming/versioning.** (§3.2)

---

*Compiled 2026-07-04 from the mir-emulator project's spec registry
(`packages/mir-emulator/src/mir_emulator/specs/registry.json`), its PDF→Swagger
conversion pipeline (`packages/mir-spec-scraper/`), and emulator workarounds
required for spec-faithfulness (`packages/mir-emulator/`). Reproduction details for
any finding are available in those sources.*
