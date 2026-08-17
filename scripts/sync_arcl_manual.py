"""Watch Omron's ARCL reference manual for new editions.

Omron publishes ARCL only as a PDF reference manual (I617-E-02); the
emulator's ``arcl_commands.json`` is a human transcription of it, with
per-command page citations recorded in ``specs/registry.json``. That makes
this watcher deliberately different from ``sync_vda5050_schemas.py``: there
is nothing to auto-vendor. A changed manual invalidates the *transcription*,
which only a human re-read can fix — so this script never writes anything.
It re-downloads the manual from the provenance URL and exits non-zero when
the bytes no longer match the recorded sha256 (Omron's "latest" URL is
stable across mirrors but silently swaps content on a new edition).

Usage:
  uv run python scripts/sync_arcl_manual.py --check   # exit 1 on drift
  uv run python scripts/sync_arcl_manual.py           # same (check is the only mode)

After a human re-verifies the transcription against the new edition, update
``source`` in packages/arcl-emulator/src/arcl_emulator/specs/registry.json
by hand (new document_id, sha256, retrieved date, pages) in the same commit
as the transcription changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "packages/arcl-emulator/src/arcl_emulator/specs/registry.json"


def _download(url: str) -> bytes:
    req = urllib.request.Request(  # noqa: S310 (https URL from the vendored registry)
        url, headers={"User-Agent": "amr-emulator-arcl-manual-sync"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        return resp.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify only; exit 1 on drift (the default and"
        " only behavior — accepted for symmetry with the other sync scripts)",
    )
    parser.parse_args(argv)

    source = json.loads(REGISTRY.read_text())["source"]
    url, pinned = source["url"], source["sha256"]
    try:
        payload = _download(url)
    except OSError as exc:
        print(f"problem: could not download the ARCL manual from {url}: {exc}", file=sys.stderr)
        return 1

    if not payload.startswith(b"%PDF"):
        print(
            f"problem: {url} no longer serves a PDF ({len(payload)} bytes,"
            f" starts {payload[:16]!r}) — the manual may have moved",
            file=sys.stderr,
        )
        return 1

    actual = hashlib.sha256(payload).hexdigest()
    if actual != pinned:
        print(
            f"problem: ARCL manual at {url} changed: sha256 {actual} != pinned {pinned}"
            f" ({source['document_id']}, retrieved {source['retrieved']}). A new edition"
            " likely shipped — re-verify the arcl_commands.json transcription against it,"
            " then update specs/registry.json in the same commit.",
            file=sys.stderr,
        )
        return 1

    print(f"ARCL manual unchanged: {source['document_id']} ({actual[:12]}…, {len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
