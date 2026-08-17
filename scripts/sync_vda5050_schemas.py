"""Vendor the official VDA5050 JSON schemas from github.com/VDA5050/VDA5050.

The VDA publishes the machine-readable message schemas in the public git
repository referenced by the recommendation itself (section 7: "JSON schemas
are available for validation in the public git repository"). This script
pins a tag of that repository and vendors the eight message schemas into
``packages/vda5050-emulator/src/vda5050_emulator/schemas/v<tag>/``, writing a
``registry.json`` with full provenance (tag, commit, upstream sha256, applied
normalizations).

Upstream files are not always strictly valid JSON (tag 3.0.0 ships trailing
commas in factsheet.schema), so a minimal, deterministic normalizer strips
trailing commas outside strings. Anything beyond that is a hard failure —
this script never "repairs" schemas.

Usage:
  uv run python scripts/sync_vda5050_schemas.py            # re-vendor pinned tags
  uv run python scripts/sync_vda5050_schemas.py --check    # exit 1 on any drift vs upstream
  uv run python scripts/sync_vda5050_schemas.py --tag 3.1.0  # vendor an additional tag

--check is what CI runs on a schedule: it re-downloads every pinned tag and
fails if the vendored files no longer match upstream (a moved tag or a new
normalization requirement), and also reports newer upstream tags so a new
protocol version is noticed the week it is published.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

UPSTREAM_REPO = "VDA5050/VDA5050"
RAW_URL = "https://raw.githubusercontent.com/{repo}/{ref}/json_schemas/{filename}"
API_TAGS_URL = "https://api.github.com/repos/{repo}/tags"
API_COMMIT_URL = "https://api.github.com/repos/{repo}/commits/{ref}"
API_LISTING_URL = "https://api.github.com/repos/{repo}/contents/json_schemas?ref={ref}"

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "packages/vda5050-emulator/src/vda5050_emulator/schemas"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "amr-emulator-schema-sync"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (https only)
        return resp.read()


def strip_trailing_commas(text: str) -> tuple[str, int]:
    """Remove commas directly preceding ``}`` or ``]`` outside of strings.

    Returns the normalized text and the number of commas removed. This is the
    single normalization we accept from upstream; the result must parse as
    strict JSON or the caller fails.
    """
    out: list[str] = []
    removed = 0
    in_string = False
    escaped = False
    pending_comma: int | None = None  # index in `out` of a comma awaiting a verdict
    for ch in text:
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            pending_comma = None
            out.append(ch)
            continue
        if ch == ",":
            pending_comma = len(out)
            out.append(ch)
            continue
        if ch in "}]" and pending_comma is not None:
            del out[pending_comma]
            removed += 1
            pending_comma = None
        elif ch not in " \t\r\n":
            pending_comma = None
        out.append(ch)
    return "".join(out), removed


def upstream_schema_files(tag: str) -> dict[str, str]:
    """Message type -> upstream filename, discovered from the tag's listing.

    Layout differs across tags: 3.x has eight ``<type>.schema`` files, 2.1.0
    has six, and 2.0.0 names one file ``factsheet.json``.
    """
    listing = json.loads(_get(API_LISTING_URL.format(repo=UPSTREAM_REPO, ref=tag)))
    files: dict[str, str] = {}
    for item in listing:
        name = item["name"]
        stem = name.removesuffix(".schema").removesuffix(".json").removesuffix(".schema")
        if item["type"] == "file" and (name.endswith((".schema", ".json"))):
            files[stem] = name
    return files


def vendor_tag(tag: str, *, check: bool) -> tuple[dict, list[str]]:
    """Download all schemas for one upstream tag. Returns (registry entry, problems)."""
    problems: list[str] = []
    commit = json.loads(_get(API_COMMIT_URL.format(repo=UPSTREAM_REPO, ref=tag)))
    entry: dict = {
        "upstream": f"https://github.com/{UPSTREAM_REPO}",
        "tag": tag,
        "commit": commit["sha"],
        "commit_date": commit["commit"]["committer"]["date"],
        "files": {},
    }
    target_dir = SCHEMAS_DIR / f"v{tag}"
    for name, filename in sorted(upstream_schema_files(tag).items()):
        raw = _get(RAW_URL.format(repo=UPSTREAM_REPO, ref=tag, filename=filename))
        normalized, removed = strip_trailing_commas(raw.decode("utf-8"))
        try:
            json.loads(normalized)
        except json.JSONDecodeError as exc:
            problems.append(f"{tag}/{name}.schema: not valid JSON after normalization: {exc}")
            continue
        entry["files"][f"{name}.schema.json"] = {
            "upstream_sha256": hashlib.sha256(raw).hexdigest(),
            "vendored_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
            "trailing_commas_removed": removed,
        }
        vendored = target_dir / f"{name}.schema.json"
        if check:
            if not vendored.exists():
                problems.append(f"{tag}/{name}.schema.json: missing locally")
            elif vendored.read_text() != normalized:
                problems.append(f"{tag}/{name}.schema.json: differs from upstream tag {tag}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            vendored.write_text(normalized)
    return entry, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify only; exit 1 on drift")
    parser.add_argument(
        "--tag", action="append", default=None, help="additional upstream tag to vendor"
    )
    args = parser.parse_args(argv)

    registry_path = SCHEMAS_DIR / "registry.json"
    registry = json.loads(registry_path.read_text()) if registry_path.exists() else {"tags": {}}
    tags = set(registry["tags"]) | set(args.tag or [])
    if not tags:
        tags = {"3.0.0"}

    all_problems: list[str] = []
    for tag in sorted(tags):
        entry, problems = vendor_tag(tag, check=args.check)
        all_problems.extend(problems)
        if not args.check and not problems:
            registry["tags"][tag] = entry

    def semver(tag: str) -> tuple[int, ...]:
        try:
            return tuple(int(part) for part in tag.split("."))
        except ValueError:
            return (0,)

    newest_vendored = max(semver(t) for t in tags)
    upstream_tags = [t["name"] for t in json.loads(_get(API_TAGS_URL.format(repo=UPSTREAM_REPO)))]
    newer = [t for t in upstream_tags if t not in tags and semver(t) > newest_vendored]
    if newer:
        print(f"note: upstream tags not vendored yet: {', '.join(newer)}")
        if args.check:
            all_problems.append(f"new upstream tags available: {', '.join(newer)}")

    if not args.check:
        registry_path.write_text(json.dumps(registry, indent=1, sort_keys=True) + "\n")
        print(f"vendored {len(tags)} tag(s) into {SCHEMAS_DIR.relative_to(REPO_ROOT)}")

    for problem in all_problems:
        print(f"problem: {problem}", file=sys.stderr)
    return 1 if all_problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
