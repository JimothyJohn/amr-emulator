"""Version parsing and the tracking-selection rule.

Rule: for every major release line that publishes REST API files, track the
latest patch of each of its newest N (default 4) minor lines. With the portal
publishing majors 2 and 3, that covers e.g. 3.8.x/3.7.x/3.6.x/3.5.x and
2.14.x/2.13.x/2.12.x/2.10.x — four API generations per large release.

Retention: once a minor line is tracked it is never rotated out by newer
minors — callers pass the already-tracked (major, minor) lines as
*keep_lines* and those stay selected forever, refreshed to their latest
published patch like every other line.
"""

from __future__ import annotations

import re
from collections.abc import Collection, Sequence

# Lookarounds instead of \b: versions are often embedded in filenames like
# mir_rest_api_2.13.3.1.zip, where "_2" has no word boundary and a naive \b
# regex latches onto "13.3.1".
VERSION_RE = re.compile(r"(?<![\d.])(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?(?!\.?\d)")


def parse_version(text: str) -> tuple[int, ...] | None:
    """Extract the first dotted version (3 or 4 parts) from *text*."""
    match = VERSION_RE.search(text)
    if not match:
        return None
    return tuple(int(g) for g in match.groups() if g is not None)


def format_version(version: tuple[int, ...]) -> str:
    return ".".join(str(p) for p in version)


def line_of(version: str) -> tuple[int, int]:
    """The (major, minor) release line of a dotted version string."""
    parts = version.split(".")
    return int(parts[0]), int(parts[1])


def select_tracked(
    versions: Sequence[tuple[int, ...]],
    minors_per_major: int = 4,
    keep_lines: Collection[tuple[int, int]] = (),
) -> list[tuple[int, ...]]:
    """Pick which of *versions* to track, newest first.

    For each major, keep the latest patch of each of its newest
    *minors_per_major* minor lines. Lines in *keep_lines* — the (major,
    minor) pairs already tracked — are always selected on top of that cap,
    at their latest published patch: once tracked, never rotated out.
    """
    unique = sorted(set(versions), reverse=True)
    keep = set(keep_lines)

    latest_per_line: dict[tuple[int, int], tuple[int, ...]] = {}
    for v in unique:
        latest_per_line.setdefault((v[0], v[1]), v)

    lines_taken: dict[int, int] = {}
    picked: list[tuple[int, ...]] = []
    for major, minor in sorted(latest_per_line, reverse=True):
        within_cap = lines_taken.get(major, 0) < minors_per_major
        if within_cap:
            lines_taken[major] = lines_taken.get(major, 0) + 1
        if within_cap or (major, minor) in keep:
            picked.append(latest_per_line[(major, minor)])

    return sorted(picked, reverse=True)
