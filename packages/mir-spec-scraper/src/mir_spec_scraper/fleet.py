"""Sync the bundled MiR Fleet Enterprise specs.

Unlike the robot REST API (PDFs behind a portal login), MiR publishes the
Fleet Integration API as native OpenAPI 3 JSON behind a public Swagger UI:

    .../MiR_Fleet_Enterprise_OpenAPI_Specification/<version>/openapi_v1.json

There is no version listing page, so discovery probes forward from the
versions already tracked: newer patches of each tracked minor, newer minors
of each tracked major, and the next majors — with a small gap tolerance so
a skipped number doesn't end discovery. Selection then applies the same rule
as the robot family: latest patch of the newest N minor lines per major,
with already-tracked minor lines kept forever (refreshed, never rotated out).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil
from pathlib import Path

import httpx

from mir_spec_scraper.versions import format_version, line_of, select_tracked

FLEET_BASE = (
    "https://supportportal.mobile-industrial-robots.com/support-files/manuals/"
    "MiR_Fleet_Enterprise_OpenAPI_Specification"
)
SPEC_FILENAME = "openapi_v1.json"
# Published beside the Integration API in every version directory; fetched
# best-effort — a missing extra never blocks tracking the version itself.
EXTRA_SPECS = (
    ("top_module", "openapi_topmodule_v1.json"),
    ("compatibility", "openapi_compatibility_v1.json"),
)
GAP_TOLERANCE = 2  # tolerate up to this many missing consecutive numbers
MAX_PROBES = 120  # hard cap on HTTP probes per sync, runaway backstop
MAX_SPEC_BYTES = 16 * 1024 * 1024


def _known_versions(registry: dict) -> set[tuple[int, ...]]:
    known = set()
    for entry in registry.get("fleet", {}).get("tracked", []):
        known.add(tuple(int(p) for p in entry["fleet_version"].split(".")))
    return known or {(1, 5, 0)}  # bootstrap point if the block is ever empty


def discover_versions(client: httpx.Client, known: set[tuple[int, ...]]) -> set[tuple[int, ...]]:
    """All fleet versions that publish a spec: the known set plus whatever
    forward-probing finds. Probes are HEAD-cheap GETs of the spec URL."""
    found = set(known)
    probes = 0

    def exists(version: tuple[int, ...]) -> bool:
        nonlocal probes
        if probes >= MAX_PROBES:
            return False
        probes += 1
        url = f"{FLEET_BASE}/{format_version(version)}/{SPEC_FILENAME}"
        try:
            response = client.head(url)
            if response.status_code == 405:  # some CDNs refuse HEAD
                response = client.get(url)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def scan(make, start: int) -> None:
        gaps, n = 0, start
        while gaps <= GAP_TOLERANCE and probes < MAX_PROBES:
            candidate = make(n)
            if candidate in found or exists(candidate):
                found.add(candidate)
                gaps = 0
            else:
                gaps += 1
            n += 1

    # Iterate to a fixpoint: a newly discovered minor line (1.5.0) must get
    # its own patch scan (1.5.1, 1.5.2, ...) in the next round.
    while probes < MAX_PROBES:
        before = len(found)
        majors = {v[0] for v in found}
        for major in sorted(majors):
            minors = {v[1] for v in found if v[0] == major}
            for minor in sorted(minors):
                top_patch = max(v[2] for v in found if v[:2] == (major, minor))
                scan(lambda n, ma=major, mi=minor: (ma, mi, n), top_patch + 1)
            scan(lambda n, ma=major: (ma, n, 0), max(minors) + 1)
        scan(lambda n: (n, 0, 0), max(majors) + 1)
        if len(found) == before:
            break
    return found


def sync_fleet(
    specs_dir: Path,
    minors_per_major: int = 4,
    dry_run: bool = False,
    client: httpx.Client | None = None,
) -> tuple[bool, str]:
    """Update the registry's fleet block from the public spec URLs.

    Returns (changed, summary). Network failure keeps prior coverage — the
    bundled specs are already official; a bad probe run must not drop them.
    """
    registry_path = specs_dir / "registry.json"
    registry = json.loads(registry_path.read_text())
    if "fleet" not in registry:
        # A registry without the family (e.g. minimal test fixtures) has not
        # opted in; never bootstrap it implicitly or probe the network for it.
        return False, "fleet: skipped (registry has no fleet block)"
    fleet = registry["fleet"]
    existing = {t["fleet_version"]: t for t in fleet.get("tracked", [])}
    lines: list[str] = []
    changed = False

    own_client = client is None
    if client is None:
        client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "mir-emulator-spec-scraper/1.0"},
        )
    try:
        try:
            available = discover_versions(client, _known_versions(registry))
        except httpx.HTTPError as exc:
            return False, f"fleet: discovery failed ({exc}); kept existing coverage"
        latest = format_version(max(available))
        majors = sorted({v[0] for v in available}, reverse=True)
        lines.append(
            f"fleet: {len(available)} versions published, latest {latest}, majors {majors}"
        )

        keep_lines = {line_of(v) for v in existing}
        targets = select_tracked(
            sorted(available), minors_per_major=minors_per_major, keep_lines=keep_lines
        )
        tracked = []
        for version in targets:
            version_str = format_version(version)
            entry = existing.get(version_str)
            if entry is not None:
                tracked.append(entry)
                continue
            url = f"{FLEET_BASE}/{version_str}/{SPEC_FILENAME}"
            try:
                response = client.get(url)
                response.raise_for_status()
                payload = response.content
                if len(payload) > MAX_SPEC_BYTES:
                    raise ValueError(f"spec exceeds {MAX_SPEC_BYTES} bytes")
                doc = json.loads(payload)
                if not str(doc.get("openapi", "")).startswith("3"):
                    raise ValueError("document is not OpenAPI 3")
            except (httpx.HTTPError, ValueError) as exc:
                lines.append(f"fleet {version_str}: skipped ({exc})")
                continue
            sha = hashlib.sha256(payload).hexdigest()
            rel = f"fleet/{version_str}/{SPEC_FILENAME}"
            if not dry_run:
                target = specs_dir / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)

            extras = []
            for extra_name, extra_filename in EXTRA_SPECS:
                extra_url = f"{FLEET_BASE}/{version_str}/{extra_filename}"
                try:
                    extra_response = client.get(extra_url)
                    extra_response.raise_for_status()
                    extra_payload = extra_response.content
                    if len(extra_payload) > MAX_SPEC_BYTES:
                        raise ValueError(f"spec exceeds {MAX_SPEC_BYTES} bytes")
                    extra_doc = json.loads(extra_payload)
                    if not str(extra_doc.get("openapi", "")).startswith("3"):
                        raise ValueError("document is not OpenAPI 3")
                except (httpx.HTTPError, ValueError) as exc:
                    lines.append(f"fleet {version_str}/{extra_name}: skipped ({exc})")
                    continue
                extra_rel = f"fleet/{version_str}/{extra_filename}"
                if not dry_run:
                    (specs_dir / extra_rel).parent.mkdir(parents=True, exist_ok=True)
                    (specs_dir / extra_rel).write_bytes(extra_payload)
                extra_sha = hashlib.sha256(extra_payload).hexdigest()
                extras.append(
                    {
                        "name": extra_name,
                        "title": extra_doc.get("info", {}).get("title", extra_name),
                        "file": extra_rel,
                        "sha256": extra_sha,
                        "official": True,
                        "source_url": extra_url,
                        "source_sha256": extra_sha,
                    }
                )

            entry = {
                "fleet_version": version_str,
                "api_path_version": "v1",
                "format": "openapi-3.0",
                "file": rel,
                "sha256": sha,
                "official": True,
                "provenance": (
                    "Official MiR Fleet Enterprise Integration API OpenAPI document, "
                    "downloaded verbatim from the public MiR support portal Swagger UI."
                ),
                "source_url": url,
                "source_sha256": sha,
            }
            if extras:
                entry["extra_apis"] = extras
            tracked.append(entry)
            changed = True
            lines.append(f"fleet: {'would add' if dry_run else 'added'} {version_str}")
    finally:
        if own_client:
            client.close()

    # A tracked version is only ever superseded by a newer patch of its own
    # minor line — never erased because the line aged out of the selection
    # window, vanished, or its replacement failed to download.
    newest_per_line: dict[tuple[int, int], list[int]] = {}
    for t in tracked:
        key = [int(p) for p in str(t["fleet_version"]).split(".")]
        newest_per_line[(key[0], key[1])] = max(newest_per_line.get((key[0], key[1]), key), key)
    present = {t["fleet_version"] for t in tracked}
    for version_str, entry in sorted(existing.items()):
        key = [int(p) for p in version_str.split(".")]
        replacement = newest_per_line.get((key[0], key[1]))
        if version_str not in present and (replacement is None or replacement < key):
            tracked.append(entry)
            lines.append(f"fleet: kept {version_str}: no replacement published")

    tracked.sort(key=lambda t: [int(p) for p in str(t["fleet_version"]).split(".")], reverse=True)
    dropped = set(existing) - {t["fleet_version"] for t in tracked}
    if dropped:
        changed = True
        lines.append(f"fleet: superseded by a newer patch: {', '.join(sorted(dropped))}")

    if changed and not dry_run:
        fleet["tracked"] = tracked
        registry["updated"] = datetime.date.today().isoformat()
        registry_path.write_text(json.dumps(registry, indent=2) + "\n")
        for version_str in dropped:
            # Each fleet version owns its directory (integration + extras).
            shutil.rmtree((specs_dir / existing[version_str]["file"]).parent, ignore_errors=True)

    if not changed:
        lines.append("fleet: no changes")
    return changed, "; ".join(lines)
