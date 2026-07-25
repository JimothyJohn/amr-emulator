"""Sync the bundled specs with the MiR support portal.

Usage (from the repo root):

    MIR_PORTAL_EMAIL=... MIR_PORTAL_PASSWORD=... mir-spec-scraper sync

The portal publishes the API definitions as PDFs only (one per product per
version); this pipeline picks one robot PDF per selected version (MIR250
preferred; FLEET and HOOK are different APIs and are excluded), converts it to
Swagger 2.0 (pdf_convert), and updates the bundled registry. Registry entries
with "pinned": true are never dropped or overwritten — that keeps the official
3.5.4 swagger.json around as the converter's correctness oracle. Tracked minor
lines are permanent: a version is only ever replaced by a newer patch of its
own line, never erased because newer minors pushed it out of the selection
window or the portal stopped publishing it.

Exit code is 0 unless something actually broke; "no credentials" and "nothing
new" are normal outcomes. Inside GitHub Actions, ``changed`` and ``summary``
are written to $GITHUB_OUTPUT so the workflow can decide whether to open a PR.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from collections.abc import Callable
from pathlib import Path

from mir_spec_scraper.portal import PortalClient, PortalFile
from mir_spec_scraper.summarize import SummaryError, summarizer_from_env
from mir_spec_scraper.versions import format_version, line_of, select_tracked

DEFAULT_SPECS_DIR = Path("packages/mir-emulator/src/mir_emulator/specs")

_PRODUCT_RE = re.compile(r"MiR_([A-Z0-9]+)_REST_API", re.IGNORECASE)
PRODUCT_PREFERENCE = ["MIR250", "MIR100", "MIR200", "MIR500", "MIR600", "MIR1000", "MIR1350"]
EXCLUDED_PRODUCTS = {"FLEET", "HOOK"}  # separate APIs, not the robot interface


def _github_output(changed: bool, summary: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    # $GITHUB_OUTPUT is line-oriented and the summary carries portal-derived
    # text; collapse whitespace so a smuggled newline can't forge extra keys.
    summary = " ".join(summary.split())
    with open(output_path, "a") as fh:
        fh.write(f"changed={'true' if changed else 'false'}\n")
        fh.write(f"summary={summary}\n")


def _product(file: PortalFile) -> str:
    match = _PRODUCT_RE.search(file.url) or _PRODUCT_RE.search(file.label)
    return match.group(1).upper() if match else ""


def _pick_file(files: list[PortalFile], version: tuple[int, ...]) -> PortalFile | None:
    candidates = [f for f in files if f.version == version and _product(f) not in EXCLUDED_PRODUCTS]

    def rank(f: PortalFile) -> tuple:
        url = f.url.lower()
        machine_readable = not url.endswith((".json", ".yaml", ".yml", ".zip"))
        product = _product(f)
        preference = (
            PRODUCT_PREFERENCE.index(product)
            if product in PRODUCT_PREFERENCE
            else len(PRODUCT_PREFERENCE)
        )
        return (machine_readable, preference, f.url)

    return min(candidates, key=rank) if candidates else None


def _extract_zip(data: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        members = [
            m
            for m in zf.namelist()
            if m.lower().endswith((".json", ".yaml", ".yml")) and not m.startswith("__MACOSX")
        ]
        if not members:
            raise ValueError("zip download contains no .json/.yaml spec")
        members.sort(key=lambda m: (not m.lower().endswith(".json"), len(m)))
        return zf.read(members[0])


def _spec_from_payload(data: bytes, version_str: str) -> tuple[bytes, str, str, list[str]]:
    """(stored bytes, file extension, format, warnings) for a portal download."""
    if data[:4] == b"PK\x03\x04":
        data = _extract_zip(data)
    if data[:5] == b"%PDF-":
        from mir_spec_scraper.pdf_convert import convert_pdf

        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(data)
            tmp.flush()
            doc = convert_pdf(tmp.name)
        warnings = list(doc.get("x-mir-converter-warnings", []))
        parsed = doc["info"].get("version", "")
        if parsed and parsed != version_str:
            warnings.append(f"PDF self-reports version {parsed!r}, expected {version_str!r}")
        return (
            json.dumps(doc, indent=1).encode() + b"\n",
            ".json",
            "swagger-2.0",
            warnings,
        )
    text = data[:2000].decode("utf-8", errors="replace")
    if '"swagger"' in text or "swagger:" in text:
        fmt = "swagger-2.0"
    elif '"openapi"' in text or "openapi:" in text:
        fmt = "openapi-3.0"
    else:
        raise ValueError("downloaded file is neither a PDF nor a swagger/openapi document")
    ext = ".json" if text.lstrip().startswith("{") else ".yaml"
    return data, ext, fmt, []


_VERSION_DIR_RE = re.compile(r"^\d+(\.\d+){2,3}$")


def _previous_spec(specs_dir: Path, existing: dict, version_str: str) -> tuple[str, dict] | None:
    """Best predecessor for a changelog: same version (re-conversion), else the
    closest older tracked version."""
    candidates = []
    for v, entry in existing.items():
        path = specs_dir / entry["file"]
        if not path.is_file() or path.suffix != ".json":
            continue
        key = tuple(int(p) for p in v.split("."))
        candidates.append((key, v, path))
    target = tuple(int(p) for p in version_str.split("."))
    same = [c for c in candidates if c[1] == version_str]
    older = sorted((c for c in candidates if c[0] < target), reverse=True)
    pick = same[0] if same else (older[0] if older else None)
    if pick is None:
        return None
    return pick[1], json.loads(pick[2].read_text())


def _fallback_entry(existing: dict, version_str: str, tracked: list[dict]) -> dict | None:
    """Closest already-known version of the same major — keeps a major line
    covered when its newest file turns out to be broken."""
    major = version_str.split(".")[0]
    taken = {t["mir_version"] for t in tracked}
    candidates = [
        (tuple(int(p) for p in v.split(".")), v)
        for v in existing
        if v.split(".")[0] == major and v not in taken
    ]
    return existing[max(candidates)[1]] if candidates else None


def sync(
    specs_dir: Path,
    minors_per_major: int,
    dry_run: bool,
    force: bool = False,
    report_path: Path | None = None,
    client: PortalClient | None = None,
    summarizer: Callable[[str], str] | None = None,
) -> tuple[bool, str]:
    if client is None:
        email = os.environ.get("MIR_PORTAL_EMAIL", "")
        password = os.environ.get("MIR_PORTAL_PASSWORD", "")
        if not email or not password:
            return False, (
                "skipped: MIR_PORTAL_EMAIL/MIR_PORTAL_PASSWORD not set "
                "(free account: supportportal.mobile-industrial-robots.com)"
            )
        client = PortalClient(email, password)

    registry_path = specs_dir / "registry.json"
    registry = json.loads(registry_path.read_text())
    existing = {t["mir_version"]: t for t in registry["tracked"]}
    pinned = {v: t for v, t in existing.items() if t.get("pinned")}
    lines: list[str] = []
    report: list[str] = []
    changed = False
    try:
        client.login()
        files = client.list_files()
        if not files:
            return False, "portal listing parsed to zero API files; parser may need updating"

        latest_seen = format_version(max(f.version for f in files))
        majors_seen = sorted({f.version[0] for f in files}, reverse=True)
        lines.append(f"portal: {len(files)} files, latest {latest_seen}, majors {majors_seen}")

        # Already-tracked minor lines are permanent: they keep refreshing to
        # their latest patch but are never rotated out by newer minors.
        keep_lines = {line_of(v) for v in existing}
        targets = select_tracked(
            [f.version for f in files],
            minors_per_major=minors_per_major,
            keep_lines=keep_lines,
        )
        tracked = []
        for version in targets:
            version_str = format_version(version)
            if not _VERSION_DIR_RE.fullmatch(version_str):
                lines.append(f"refusing suspicious version string {version_str!r}")
                continue
            if version_str in pinned:
                continue  # pinned entries are authoritative for their version
            portal_file = _pick_file(files, version)
            if portal_file is None:
                lines.append(f"no usable robot API file for {version_str}; skipped")
                if version_str in existing:
                    tracked.append(existing[version_str])
                continue

            entry = existing.get(version_str)
            try:
                payload = client.download(portal_file)
                source_sha = hashlib.sha256(payload).hexdigest()
                if entry and entry.get("source_sha256") == source_sha and not force:
                    tracked.append(entry)
                    continue
                stored, ext, fmt, warnings = _spec_from_payload(payload, version_str)
            except (ValueError, OSError) as exc:
                # One broken file must not kill the whole sync — keep prior
                # coverage of this version (or its major) and say so loudly.
                lines.append(f"kept previous spec for {version_str}; error: {exc}")
                kept = entry or _fallback_entry(existing, version_str, tracked)
                if kept:
                    tracked.append(kept)
                continue
            if warnings:
                lines.append(
                    f"kept previous spec for {version_str}; conversion warnings: "
                    + "; ".join(warnings)
                )
                kept = entry or _fallback_entry(existing, version_str, tracked)
                if kept:
                    tracked.append(kept)
                continue

            rel = f"{version_str}/swagger{ext}"
            if ext == ".json":
                previous = _previous_spec(specs_dir, existing, version_str)
                if previous:
                    from mir_spec_scraper.diff import api_diff_markdown

                    old_label, old_doc = previous
                    report.append(
                        api_diff_markdown(old_doc, json.loads(stored), old_label, version_str)
                    )
            if not dry_run:
                target_path = specs_dir / rel
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(stored)
            tracked.append(
                {
                    "mir_version": version_str,
                    "api_path_version": "v2.0.0",
                    "format": fmt,
                    "file": rel,
                    "sha256": hashlib.sha256(stored).hexdigest(),
                    "official": True,
                    "provenance": (
                        f"Converted from the official MiR REST API PDF: {portal_file.url}"
                        if payload[:5] == b"%PDF-"
                        else f"MiR support portal: {portal_file.url}"
                    ),
                    "source_url": portal_file.url,
                    "source_sha256": source_sha,
                }
            )
            changed = True
            lines.append(
                f"{'would add' if dry_run else 'added'} {version_str} from {portal_file.url}"
            )

        tracked.extend(pinned.values())
        # A tracked version is only ever superseded by a newer patch of its
        # own minor line — never erased because the line aged out of the
        # selection window or vanished from the portal.
        newest_per_line: dict[tuple[int, int], list[int]] = {}
        for t in tracked:
            key = [int(p) for p in str(t["mir_version"]).split(".")]
            newest_per_line[(key[0], key[1])] = max(newest_per_line.get((key[0], key[1]), key), key)
        present = {t["mir_version"] for t in tracked}
        for version_str, entry in sorted(existing.items()):
            key = [int(p) for p in version_str.split(".")]
            replacement = newest_per_line.get((key[0], key[1]))
            if version_str not in present and (replacement is None or replacement < key):
                tracked.append(entry)
                lines.append(f"kept {version_str}: no replacement published on the portal")
        tracked.sort(key=lambda t: [int(p) for p in str(t["mir_version"]).split(".")], reverse=True)
    finally:
        client.close()

    dropped = set(existing) - {t["mir_version"] for t in tracked}
    if dropped:
        changed = True
        lines.append(f"superseded by a newer patch: {', '.join(sorted(dropped))}")

    if changed and not dry_run:
        registry["tracked"] = tracked
        registry["updated"] = datetime.date.today().isoformat()
        registry["wanted"] = []
        registry_path.write_text(json.dumps(registry, indent=2) + "\n")
        for version_str in dropped:
            old = existing[version_str]["file"].split("/")[0]
            shutil.rmtree(specs_dir / old, ignore_errors=True)

    if report_path is not None:
        body = "\n\n".join(report) if report else "_No spec changes this run._\n"
        if summarizer is None:
            summarizer = summarizer_from_env()
        if report and summarizer is not None:
            try:
                summary_md = summarizer(body)
                body = f"### Release impact (AI-generated)\n\n{summary_md}\n\n---\n\n{body}"
            except SummaryError as exc:
                lines.append(f"AI summary skipped: {exc}")
        report_path.write_text(f"## Scrape report\n\n{'; '.join(lines)}\n\n{body}")

    if not changed:
        lines.append("no spec changes: portal matches tracked specs")
    summary = "; ".join(lines)
    return changed, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mir-spec-scraper")
    sub = parser.add_subparsers(dest="command", required=True)
    p_sync = sub.add_parser("sync", help="fetch portal listing and update bundled specs")
    p_sync.add_argument("--specs-dir", type=Path, default=DEFAULT_SPECS_DIR)
    p_sync.add_argument(
        "--minors-per-major",
        type=int,
        default=4,
        help="latest patch of this many minor lines per major release (default 4)",
    )
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.add_argument(
        "--force",
        action="store_true",
        help="re-convert even when the source file is unchanged (converter upgrades)",
    )
    p_sync.add_argument(
        "--report",
        type=Path,
        default=None,
        help="write a markdown scrape report (API changelog) to this path",
    )
    args = parser.parse_args(argv)

    if not (args.specs_dir / "registry.json").is_file():
        print(
            f"error: no registry.json under {args.specs_dir} (run from the repo root?)",
            file=sys.stderr,
        )
        return 2

    changed, summary = sync(
        args.specs_dir,
        args.minors_per_major,
        args.dry_run,
        force=args.force,
        report_path=args.report,
    )

    # The Fleet Enterprise specs are public OpenAPI JSON (no credentials), so
    # this half of the sync runs even when the portal half is skipped.
    from mir_spec_scraper.fleet import sync_fleet

    fleet_changed, fleet_summary = sync_fleet(args.specs_dir, args.minors_per_major, args.dry_run)
    changed = changed or fleet_changed
    summary = f"{summary}; {fleet_summary}"

    print(summary)
    _github_output(changed, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
