# External validation: Mission Dispatch → mir-vda5050-adapter → mir-emulator

Date: 2026-08-16 · branch `feat/vda5050-emulator` · Mission Dispatch 4.3.0

The point of the adapter: any VDA 5050 master control can drive a MiR robot.
Proven live with the full triangle — NVIDIA Isaac Mission Dispatch (external
master) → `mir-vda5050-adapter` (VDA 5050 2.0.0 ↔ MiR REST 3.8.1) →
`mir-emulator` (spec-faithful MiR robot). The adapter translated MD's route
orders into MiR missions (positions + move actions + mission_queue), tracked
execution by polling `GET /status`, and published spec-valid state back.

## Transcript (mission summary)

```
t+  0.03s [MD api ] robot carter01 online=True battery=92.5% pose=(5.00,5.00)
t+  0.04s [MD api ] mission s44hx4rs25cillcask5t4qgdte submitted (2 route nodes, 3 waypoints total)
t+  0.04s [MD api ] mission PENDING nodes={'goto_pickup': 'PENDING', 'goto_dropoff': 'PENDING'}
t+  1.07s [MD api ] mission RUNNING nodes={'goto_pickup': 'PENDING', 'goto_dropoff': 'PENDING'}
t+  6.18s [MD api ] mission RUNNING nodes={'goto_pickup': 'COMPLETED', 'goto_dropoff': 'PENDING'}
t+ 11.32s [MD api ] mission COMPLETED nodes={'goto_pickup': 'COMPLETED', 'goto_dropoff': 'COMPLETED'}
t+ 11.32s [MD api ] final robot pose=(5.00,6.50) state=IDLE
RESULT: mission COMPLETED
```

MD log: mission `s44hx4rs25cillcask5t4qgdte` COMPLETED in ~11s; robot
`ON_TASK -> IDLE`; final pose (5.00, 6.50) — the MiR emulator's actual pose,
reported through the adapter.

## What the live run caught (both fixed + regression-tested)

1. **Vacuous 2.0.0 schema defeated the 1.x compat path**: the official 2.0.0
   instantActions schema has no `required` fields, so MD's 1.x-shaped
   messages validated cleanly and the compat fallback (keyed on schema
   problems) never ran — actions were silently ignored. The fallback now
   keys on the missing `actions` field (`test_compat.py::
   test_legacy_field_works_on_2_0_0_despite_vacuous_schema`).
2. **Pose sampling can skip a waypoint**: at 0.5s polling and ~1 m/s, the
   robot can cross a 0.3 m deviation window between polls, so head-of-line
   traversal detection stalled. Traversal is now monotone (reaching a later
   node implies earlier ones) and MiR mission completion marks all remaining
   released nodes traversed.

## Reproduce

```
uv run mir-emulator --port 8080 --mission-duration 4
uv run vda5050-emulator --robots 0 --port 1884          # broker-only
uv run mir-vda5050-adapter --broker 127.0.0.1:1884 \
    --manufacturer RobotCompany --serial carter01
# then the Mission Dispatch stack + driver from isaac-mission-dispatch/
```
