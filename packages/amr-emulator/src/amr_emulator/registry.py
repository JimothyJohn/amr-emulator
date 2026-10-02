"""Access to the bundled spec registry (specs/registry.json)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path


@dataclass(frozen=True)
class TrackedSpec:
    mir_version: str
    format: str
    file: str
    sha256: str
    official: bool
    provenance: str


def _specs_dir() -> Path:
    return Path(str(resources.files("amr_emulator").joinpath("specs")))


def load_registry() -> dict:
    return json.loads((_specs_dir() / "registry.json").read_text())


def primary_source() -> str:
    """The MiR support portal page the tracked specs are scraped from."""
    return load_registry()["source"]


def tracked_entry(mir_version: str) -> dict:
    """The raw registry record for one tracked version (provenance, hashes)."""
    for entry in load_registry()["tracked"]:
        if entry["mir_version"] == mir_version:
            return entry
    raise KeyError(f"MiR version {mir_version!r} is not tracked")


def tracked_specs() -> list[TrackedSpec]:
    return [
        TrackedSpec(
            mir_version=t["mir_version"],
            format=t["format"],
            file=t["file"],
            sha256=t["sha256"],
            official=t["official"],
            provenance=t["provenance"],
        )
        for t in load_registry()["tracked"]
    ]


def version_key(version: str) -> tuple[int, ...]:
    """Sort key for dotted numeric versions, tolerating 4-part MiR versions."""
    return tuple(int(p) for p in version.split("."))


def supported_versions() -> list[str]:
    """Tracked MiR versions, newest first."""
    return sorted((t.mir_version for t in tracked_specs()), key=version_key, reverse=True)


def fleet_registry() -> dict:
    """The MiR Fleet Enterprise family block (empty dict if absent)."""
    return load_registry().get("fleet", {})


def fleet_tracked_entry(fleet_version: str) -> dict:
    for entry in fleet_registry().get("tracked", []):
        if entry["fleet_version"] == fleet_version:
            return entry
    raise KeyError(f"Fleet version {fleet_version!r} is not tracked")


def fleet_supported_versions() -> list[str]:
    """Tracked MiR Fleet versions, newest first."""
    versions = (t["fleet_version"] for t in fleet_registry().get("tracked", []))
    return sorted(versions, key=version_key, reverse=True)


def fleet_extra_specs(fleet_version: str) -> list[dict]:
    """The Top Module / Compatibility API records for one fleet version, each
    with a resolved absolute "path" key added (empty list if none tracked)."""
    entry = fleet_tracked_entry(fleet_version)
    extras = []
    for record in entry.get("extra_apis", []):
        extras.append({**record, "path": _specs_dir() / record["file"]})
    return extras


def fleet_spec_path(fleet_version: str | None = None) -> tuple[str, Path]:
    """Resolve a Fleet version (or the newest) to its bundled spec file."""
    entries = {t["fleet_version"]: t for t in fleet_registry().get("tracked", [])}
    if not entries:
        raise KeyError("no MiR Fleet versions are tracked in this build")
    if fleet_version is None:
        fleet_version = fleet_supported_versions()[0]
    if fleet_version not in entries:
        raise KeyError(
            f"Fleet version {fleet_version!r} is not tracked; "
            f"available: {fleet_supported_versions()}"
        )
    return fleet_version, _specs_dir() / entries[fleet_version]["file"]


def spec_path(mir_version: str | None = None) -> tuple[str, Path]:
    """Resolve a MiR version (or the default) to its bundled spec file.

    Returns (resolved_version, path). Raises KeyError for unknown versions.
    """
    specs = {t.mir_version: t for t in tracked_specs()}
    if mir_version is None:
        from amr_emulator._version import DEFAULT_MIR_VERSION

        mir_version = DEFAULT_MIR_VERSION or supported_versions()[0]
    if mir_version not in specs:
        raise KeyError(
            f"MiR version {mir_version!r} is not tracked; available: {supported_versions()}"
        )
    return mir_version, _specs_dir() / specs[mir_version].file
