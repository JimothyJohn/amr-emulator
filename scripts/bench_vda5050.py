"""Performance baseline for the embedded VDA 5050 MQTT stack.

One command, repeatable numbers (TODO.md "Performance baseline before
performance work"): boots the real Broker and N real VirtualAGVs with a
pinned message mix — periodic state + visualization at fixed intervals plus
a constant-rate latency probe — and reports:

  - publish→receive latency through the broker (p50 / p99 / max, ms),
    measured by a dedicated probe pair (one client publishes timestamped
    payloads, another subscribed client timestamps arrival, same process
    and event loop — so numbers include our client stack, deliberately);
  - fan-out throughput: robot messages/sec observed by a wildcard
    subscriber across all N robots;
  - memory: peak RSS, plus Python heap growth per minute (tracemalloc
    deltas between the run's first and second half) — the soak signal.

Usage:
  uv run python scripts/bench_vda5050.py                       # default: 10 robots, 30 s
  uv run python scripts/bench_vda5050.py --robots 50 --duration 60
  uv run python scripts/bench_vda5050.py --duration 7200       # multi-hour soak
  uv run python scripts/bench_vda5050.py --json docs/bench/baseline.json

The committed baseline lives at docs/bench/baseline.json (host recorded
inside; regressions are judged against the same host class). The mix is
idle robots — order execution adds evaluator cost on top of this floor and
can be layered in when there is an order-throughput question to answer.
"""

from __future__ import annotations

import argparse
import array
import asyncio
import contextlib
import json
import platform
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

from vda5050_emulator import AGVConfig, Broker, MQTTClient, VirtualAGV

PROBE_TOPIC = "bench/probe"
# Pinned mix: every robot publishes state every 1.0 s and visualization
# every 0.5 s (wall time; SimClock default scale is 1.0).
STATE_INTERVAL = 1.0
VISUALIZATION_INTERVAL = 0.5


def _rss_peak_bytes() -> int:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes, Linux kibibytes.
    return peak if sys.platform == "darwin" else peak * 1024


async def run_bench(robots: int, duration: float, probe_rate: float, version: str) -> dict:
    broker = Broker(port=0)
    await broker.start()

    fleet: list[VirtualAGV] = []
    for n in range(robots):
        config = AGVConfig(
            version=version,
            serial_number=f"bench-{n:04d}",
            default_state_interval=STATE_INTERVAL,
            visualization_interval=VISUALIZATION_INTERVAL,
        )
        robot = VirtualAGV(config, port=broker.port)
        await robot.start()
        fleet.append(robot)

    watcher = MQTTClient("bench-watcher", "127.0.0.1", broker.port)
    await watcher.connect()
    await watcher.subscribe("#")

    prober = MQTTClient("bench-prober", "127.0.0.1", broker.port)
    await prober.connect()

    # array('q') so the probe buffer's own growth is exactly 8 bytes/sample
    # and can be subtracted from the heap-growth soak signal.
    latencies_ns = array.array("q")
    robot_messages = 0
    probe_interval = 1.0 / probe_rate

    async def watch() -> None:
        nonlocal robot_messages
        while True:
            message = await watcher.messages.get()
            if message.topic == PROBE_TOPIC:
                sent_ns = int(message.payload)
                latencies_ns.append(time.perf_counter_ns() - sent_ns)
            else:
                robot_messages += 1

    async def probe() -> None:
        while True:
            await prober.publish(PROBE_TOPIC, str(time.perf_counter_ns()).encode())
            await asyncio.sleep(probe_interval)

    tracemalloc.start()
    watch_task = asyncio.create_task(watch())
    probe_task = asyncio.create_task(probe())

    started = time.perf_counter()
    await asyncio.sleep(duration / 2)
    heap_mid, _ = tracemalloc.get_traced_memory()
    mid_messages = robot_messages
    mid_samples = len(latencies_ns)
    mid_time = time.perf_counter()
    await asyncio.sleep(duration / 2)
    heap_end, _ = tracemalloc.get_traced_memory()
    elapsed = time.perf_counter() - started
    probe_buffer_growth = (len(latencies_ns) - mid_samples) * latencies_ns.itemsize
    tracemalloc.stop()

    probe_task.cancel()
    watch_task.cancel()
    for task in (probe_task, watch_task):
        with contextlib.suppress(asyncio.CancelledError):
            await task
    await prober.disconnect()
    await watcher.disconnect()
    for robot in fleet:
        await robot.stop()
    await broker.stop()

    lat_ms = sorted(ns / 1e6 for ns in latencies_ns)
    second_half_minutes = (elapsed - (mid_time - started)) / 60
    return {
        "config": {
            "robots": robots,
            "duration_s": round(elapsed, 1),
            "probe_rate_hz": probe_rate,
            "state_interval_s": STATE_INTERVAL,
            "visualization_interval_s": VISUALIZATION_INTERVAL,
            "vda5050_version": version,
        },
        "latency_ms": {
            "samples": len(lat_ms),
            "p50": round(statistics.median(lat_ms), 3) if lat_ms else None,
            "p99": round(lat_ms[int(len(lat_ms) * 0.99) - 1], 3) if len(lat_ms) >= 100 else None,
            "max": round(lat_ms[-1], 3) if lat_ms else None,
        },
        "throughput": {
            "robot_messages": robot_messages,
            "messages_per_s": round(robot_messages / elapsed, 1),
            "second_half_messages_per_s": round(
                (robot_messages - mid_messages) / (elapsed - (mid_time - started)), 1
            ),
        },
        "memory": {
            "rss_peak_mib": round(_rss_peak_bytes() / (1024 * 1024), 1),
            "heap_mid_mib": round(heap_mid / (1024 * 1024), 2),
            "heap_end_mib": round(heap_end / (1024 * 1024), 2),
            # Excludes the bench's own latency-sample buffer; this is the
            # emulator-stack soak signal and should sit at ~0.
            "heap_growth_mib_per_min": round(
                (heap_end - heap_mid - probe_buffer_growth)
                / (1024 * 1024)
                / max(second_half_minutes, 1e-9),
                3,
            ),
        },
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "commit": subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607 - fixed argv
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip(),
            "date": time.strftime("%Y-%m-%d"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--robots", type=int, default=10)
    parser.add_argument("--duration", type=float, default=30.0, help="seconds; use hours for soak")
    parser.add_argument("--probe-rate", type=float, default=50.0, help="latency probes per second")
    parser.add_argument("--version", default="3.0.0", help="VDA 5050 protocol version")
    parser.add_argument("--json", type=Path, help="also write the report as JSON to this path")
    args = parser.parse_args()

    report = asyncio.run(run_bench(args.robots, args.duration, args.probe_rate, args.version))

    latency = report["latency_ms"]
    throughput = report["throughput"]
    memory = report["memory"]
    print(
        f"{report['config']['robots']} robots, {report['config']['duration_s']}s "
        f"(VDA {report['config']['vda5050_version']})\n"
        f"latency   p50 {latency['p50']} ms  p99 {latency['p99']} ms  "
        f"max {latency['max']} ms  ({latency['samples']} probes)\n"
        f"fan-out   {throughput['messages_per_s']} robot msgs/s "
        f"(second half {throughput['second_half_messages_per_s']}/s)\n"
        f"memory    RSS peak {memory['rss_peak_mib']} MiB, heap growth "
        f"{memory['heap_growth_mib_per_min']} MiB/min"
    )
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n")
        print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
