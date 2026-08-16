"""Simulated time for the virtual AGV.

All robot logic operates in *simulated* seconds. ``SimClock`` maps simulated
time onto wall time with a configurable scale (``--time-scale``), so missions
keep realistic simulated durations and timestamps while tests wait
milliseconds. ``ManualClock`` removes wall time entirely: sleepers only wake
when the test calls ``advance()``, which is what makes the unit suite
deterministic (no real sleeps, no flakes).
"""

from __future__ import annotations

import asyncio
import heapq
import time as _time
from datetime import UTC, datetime


def iso(sim_epoch: float) -> str:
    """ISO 8601 UTC with milliseconds, the format mandated by the spec."""
    return datetime.fromtimestamp(sim_epoch, tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class SimClock:
    """Wall-clock backed simulated time, ``scale`` sim-seconds per wall second."""

    def __init__(self, scale: float = 1.0, start: float | None = None) -> None:
        if scale <= 0:
            raise ValueError("time scale must be > 0")
        self._scale = scale
        self._sim_anchor = _time.time() if start is None else start
        self._wall_anchor = _time.monotonic()

    @property
    def scale(self) -> float:
        return self._scale

    def set_scale(self, scale: float) -> None:
        if scale <= 0:
            raise ValueError("time scale must be > 0")
        self._sim_anchor = self.time()
        self._wall_anchor = _time.monotonic()
        self._scale = scale

    def time(self) -> float:
        return self._sim_anchor + (_time.monotonic() - self._wall_anchor) * self._scale

    def now_iso(self) -> str:
        return iso(self.time())

    async def sleep(self, sim_seconds: float) -> None:
        if sim_seconds > 0:
            await asyncio.sleep(sim_seconds / self._scale)


class ManualClock(SimClock):
    """Deterministic clock: time only moves when ``advance()`` is called."""

    def __init__(self, start: float = 1_700_000_000.0) -> None:
        super().__init__(scale=1.0, start=start)
        self._now = start
        self._waiters: list[tuple[float, int, asyncio.Event]] = []
        self._seq = 0

    def time(self) -> float:
        return self._now

    def set_scale(self, scale: float) -> None:  # scale is meaningless here
        pass

    def advance(self, sim_seconds: float) -> None:
        self._now += sim_seconds
        while self._waiters and self._waiters[0][0] <= self._now:
            _, _, event = heapq.heappop(self._waiters)
            event.set()

    async def sleep(self, sim_seconds: float) -> None:
        if sim_seconds <= 0:
            await asyncio.sleep(0)
            return
        event = asyncio.Event()
        self._seq += 1
        heapq.heappush(self._waiters, (self._now + sim_seconds, self._seq, event))
        await event.wait()
