# Ready-to-file issues for VDA5050/VDA5050

Five schema defects this repo carries documented workarounds for (see
`registry.json`, `factsheet.py`, and `scripts/sync_vda5050_schemas.py`).
Each section is a complete issue body — file them verbatim at
<https://github.com/VDA5050/VDA5050/issues>, then record each issue URL in
`registry.json` next to the corresponding normalization/note so the weekly
sync can tell us when a workaround can be retired.

---

## Issue 1 — tag 3.0.0: three schemas are not valid JSON (trailing commas)

**Title:** `3.0.0 schemas contain trailing commas and fail to parse as JSON`

At tag 3.0.0, `factsheet.schema` (4 occurrences), `order.schema` (1) and
`visualization.schema` (2) contain trailing commas, so any
standards-compliant JSON parser rejects them outright — every consumer has
to repair the files before they can validate a single message. Please
re-release the tag's schemas as valid JSON (a CI check that `json.load`s
every schema on push would prevent regressions).

---

## Issue 2 — tag 3.0.0 factsheet: `required` names `mobileRobotKinematic`, the property is `mobileRobotKinematics`

**Title:** `factsheet.schema 3.0.0: required key mobileRobotKinematic doesn't match defined property mobileRobotKinematics`

`typeSpecification.required` lists `mobileRobotKinematic` (singular) while
the defined property — and the PDF's table — is `mobileRobotKinematics`
(plural). A factsheet using the documented property name fails validation;
strictly, a conforming document must carry **both** spellings. One of the
two needs to change (presumably `required`).

---

## Issue 3 — tag 3.0.0 factsheet: `pauseAllowed` / `cancelAllowed` typed string, PDF says boolean

**Title:** `factsheet.schema 3.0.0: agvActions pauseAllowed/cancelAllowed are type string but documented as boolean`

The PDF describes both fields as booleans; the schema types them as
strings. On the wire the schema wins, so implementations must publish
`"true"` / `"false"` strings — and consumers written from the PDF break.
Please align the schema with the prose (type boolean) or vice versa.

---

## Issue 4 — tag 2.1.0 factsheet: unsatisfiable `enum` on the `blockingTypes` array

**Title:** `factsheet.schema 2.1.0: blockingTypes has a scalar enum on an array — no value can validate`

`agvActions[].blockingTypes` is typed `array` but carries a scalar `enum`
of the individual blocking types, which no array value can ever satisfy.
Any factsheet that includes the (optional) field is invalid by
construction; the only conforming move is omitting it, which defeats the
field's purpose. The enum presumably belongs on `items`.

---

## Issue 5 — tag 2.0.0 factsheet schema is structurally vacuous

**Title:** `factsheet.schema 2.0.0 validates any JSON object (no required, no property constraints)`

The 2.0.0 factsheet schema declares no required fields and no meaningful
property constraints, so `{}` — or any unrelated object — validates. It
cannot catch a single conformance error, and tools that gate behavior on
"factsheet validates" silently pass everything. If 2.0.0 is still meant to
be implementable, the schema needs the documented structure; otherwise a
deprecation note in the repo would spare integrators the discovery.
