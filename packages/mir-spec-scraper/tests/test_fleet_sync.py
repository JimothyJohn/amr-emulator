"""Fleet spec sync: discovery probing, selection, and registry updates —
exercised offline via an httpx.MockTransport standing in for the portal CDN."""

import json
from pathlib import Path

import httpx
import pytest
from mir_spec_scraper.fleet import FLEET_BASE, discover_versions, sync_fleet


def _openapi(version: str) -> bytes:
    return json.dumps(
        {
            "openapi": "3.0.4",
            "info": {"title": "MiR Fleet Integration API v1", "version": "v1"},
            "paths": {"/healthz": {"get": {"responses": {"200": {"description": "ok"}}}}},
        }
    ).encode()


def _client(published: dict[str, bytes]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        for version, payload in published.items():
            if str(request.url) == f"{FLEET_BASE}/{version}/openapi_v1.json":
                if request.method == "HEAD":
                    return httpx.Response(200)
                return httpx.Response(200, content=payload)
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.fixture
def specs_dir(tmp_path: Path) -> Path:
    d = tmp_path / "specs"
    d.mkdir()
    (d / "registry.json").write_text(
        json.dumps(
            {
                "tracked": [],
                "fleet": {
                    "source": FLEET_BASE + "/",
                    "tracked": [
                        {
                            "fleet_version": "1.3.0",
                            "api_path_version": "v1",
                            "format": "openapi-3.0",
                            "file": "fleet/1.3.0/openapi_v1.json",
                            "sha256": "x",
                            "official": True,
                            "provenance": "seed",
                        }
                    ],
                },
            }
        )
        + "\n"
    )
    (d / "fleet" / "1.3.0").mkdir(parents=True)
    (d / "fleet" / "1.3.0" / "openapi_v1.json").write_bytes(_openapi("1.3.0"))
    return d


def _registry(specs_dir: Path) -> dict:
    return json.loads((specs_dir / "registry.json").read_text())


def test_discovery_probes_past_gaps():
    published = {v: _openapi(v) for v in ["1.3.0", "1.4.0", "1.5.0", "1.5.2", "2.0.0"]}
    with _client(published) as client:
        found = discover_versions(client, {(1, 3, 0)})
    assert (1, 5, 2) in found  # 1.5.1 missing: patch gap crossed
    assert (2, 0, 0) in found  # next major found


def test_sync_adds_new_versions_and_keeps_files(specs_dir):
    published = {v: _openapi(v) for v in ["1.3.0", "1.4.0", "1.5.0"]}
    changed, summary = sync_fleet(specs_dir, client=_client(published))
    assert changed
    tracked = [t["fleet_version"] for t in _registry(specs_dir)["fleet"]["tracked"]]
    assert tracked == ["1.5.0", "1.4.0", "1.3.0"]
    for version in ("1.4.0", "1.5.0"):
        assert (specs_dir / "fleet" / version / "openapi_v1.json").is_file()
    assert "added 1.5.0" in summary


def test_resync_is_idempotent(specs_dir):
    published = {v: _openapi(v) for v in ["1.3.0", "1.4.0"]}
    sync_fleet(specs_dir, client=_client(published))
    changed, summary = sync_fleet(specs_dir, client=_client(published))
    assert not changed
    assert "no changes" in summary


def test_tracked_minor_line_survives_newer_minors(specs_dir):
    """The seeded 1.3 line stays tracked even once it falls outside the
    newest-4 window — once tracked, never rotated out."""
    published = {f"1.{m}.0": _openapi(f"1.{m}.0") for m in range(3, 9)}  # 1.3..1.8
    changed, _ = sync_fleet(specs_dir, client=_client(published))
    assert changed
    tracked = [t["fleet_version"] for t in _registry(specs_dir)["fleet"]["tracked"]]
    assert tracked == ["1.8.0", "1.7.0", "1.6.0", "1.5.0", "1.3.0"]
    assert (specs_dir / "fleet" / "1.3.0" / "openapi_v1.json").is_file()


def test_old_tracked_line_still_gets_patch_updates(specs_dir):
    published = {f"1.{m}.0": _openapi(f"1.{m}.0") for m in range(4, 9)}
    published["1.3.1"] = _openapi("1.3.1")  # newer patch of the old 1.3 line
    changed, _ = sync_fleet(specs_dir, client=_client(published))
    assert changed
    tracked = [t["fleet_version"] for t in _registry(specs_dir)["fleet"]["tracked"]]
    assert "1.3.1" in tracked and "1.3.0" not in tracked
    assert (specs_dir / "fleet" / "1.3.1" / "openapi_v1.json").is_file()
    assert not (specs_dir / "fleet" / "1.3.0").exists(), "superseded patch pruned"


def test_non_openapi_payload_is_skipped(specs_dir):
    published = {
        "1.3.0": _openapi("1.3.0"),
        "1.4.0": b"<html>login page</html>",
    }
    changed, summary = sync_fleet(specs_dir, client=_client(published))
    assert "1.4.0: skipped" in summary
    tracked = [t["fleet_version"] for t in _registry(specs_dir)["fleet"]["tracked"]]
    assert tracked == ["1.3.0"]
    assert not changed


def test_dry_run_writes_nothing(specs_dir):
    published = {v: _openapi(v) for v in ["1.3.0", "1.4.0"]}
    changed, _ = sync_fleet(specs_dir, dry_run=True, client=_client(published))
    assert changed
    assert not (specs_dir / "fleet" / "1.4.0").exists()
    tracked = [t["fleet_version"] for t in _registry(specs_dir)["fleet"]["tracked"]]
    assert tracked == ["1.3.0"]


def test_network_failure_keeps_existing_coverage(specs_dir):
    def explode(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("cdn down")

    client = httpx.Client(transport=httpx.MockTransport(explode))
    changed, summary = sync_fleet(specs_dir, client=client)
    assert not changed
    tracked = [t["fleet_version"] for t in _registry(specs_dir)["fleet"]["tracked"]]
    assert tracked == ["1.3.0"]
    assert "kept existing coverage" in summary or "no changes" in summary


def _client_with_extras(
    published: dict[str, bytes], extras: "set[str] | frozenset[str]" = frozenset()
) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        for version, payload in published.items():
            if url == f"{FLEET_BASE}/{version}/openapi_v1.json":
                return (
                    httpx.Response(200, content=payload)
                    if request.method == "GET"
                    else httpx.Response(200)
                )
            if version in extras:
                for fname in ("openapi_topmodule_v1.json", "openapi_compatibility_v1.json"):
                    if url == f"{FLEET_BASE}/{version}/{fname}":
                        return httpx.Response(200, content=payload)
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_sync_records_extra_apis_when_published(specs_dir):
    published = {"1.3.0": _openapi("1.3.0"), "1.4.0": _openapi("1.4.0")}
    changed, _summary = sync_fleet(
        specs_dir, client=_client_with_extras(published, extras={"1.4.0"})
    )
    assert changed
    entries = {t["fleet_version"]: t for t in _registry(specs_dir)["fleet"]["tracked"]}
    extras = entries["1.4.0"].get("extra_apis", [])
    assert [e["name"] for e in extras] == ["top_module", "compatibility"]
    for extra in extras:
        assert (specs_dir / extra["file"]).is_file()


def test_missing_extras_never_block_the_version(specs_dir):
    published = {"1.3.0": _openapi("1.3.0"), "1.4.0": _openapi("1.4.0")}
    changed, summary = sync_fleet(specs_dir, client=_client_with_extras(published))
    assert changed
    entries = {t["fleet_version"]: t for t in _registry(specs_dir)["fleet"]["tracked"]}
    assert "1.4.0" in entries
    assert "extra_apis" not in entries["1.4.0"]
    assert "top_module: skipped" in summary


def test_superseded_patch_directory_is_fully_pruned(specs_dir):
    published = {"1.3.0": _openapi("1.3.0")}
    sync_fleet(specs_dir, client=_client_with_extras(published, extras={"1.3.0"}))
    published = {"1.3.1": _openapi("1.3.1")}
    sync_fleet(specs_dir, client=_client_with_extras(published))
    assert not (specs_dir / "fleet" / "1.3.0").exists()
    assert (specs_dir / "fleet" / "1.3.1" / "openapi_v1.json").is_file()


def test_failed_replacement_patch_keeps_the_old_entry(specs_dir):
    """If the newer patch of a tracked line can't be fetched, the line keeps
    its previous spec instead of losing coverage."""
    published = {"1.3.1": b"<html>login page</html>", "1.4.0": _openapi("1.4.0")}
    _changed, summary = sync_fleet(specs_dir, client=_client(published))
    assert "1.3.1: skipped" in summary
    tracked = [t["fleet_version"] for t in _registry(specs_dir)["fleet"]["tracked"]]
    assert "1.3.0" in tracked, "old patch must survive a broken replacement"
    assert (specs_dir / "fleet" / "1.3.0" / "openapi_v1.json").is_file()
