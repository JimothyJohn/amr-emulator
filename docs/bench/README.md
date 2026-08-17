# VDA 5050 stack performance baselines

Produced by `uv run python scripts/bench_vda5050.py --json <file>` — the
repeatable bench over the real embedded Broker and real VirtualAGVs with a
pinned message mix (state every 1.0 s, visualization every 0.5 s per robot,
50 Hz latency probe). Host and commit are recorded inside each file;
compare like-for-like.

- `baseline.json` — 10 robots, 60 s: the canonical numbers to regress
  against.
- `baseline-50robots.json` — 50 robots, 60 s: fan-out scaling point.
- `soak-8min.json` — 10 robots, 8 min: memory-growth signal over a longer
  window. A dedicated multi-hour soak (`--duration 7200`) on a quiet
  machine is still owed for the TODO checkbox.

Regression rule of thumb: p50/p99 latency or messages/sec worse by >2x on
the same host class, or heap growth that scales with duration, is a
regression — bisect before optimizing anything else.
