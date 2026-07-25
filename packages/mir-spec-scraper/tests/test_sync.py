"""The sync state machine, exercised offline via an httpx.MockTransport portal.

The transport is a test seam only — real portal behavior is covered by the
live_portal-marked tests. These tests own the logic the live tests can't
safely exercise: pinning, dropping, idempotency, force, and broken files.
"""

import json
from pathlib import Path

import httpx
import pytest
from mir_spec_scraper.cli import sync
from mir_spec_scraper.portal import FILES_PAGE, PORTAL_BASE, PortalClient

MEDIA = "/media/rest-api"


def _swagger(version: str, extra_op: bool = False) -> bytes:
    doc = {
        "swagger": "2.0",
        "info": {"title": f"{version} MIR250 REST API", "version": version},
        "basePath": "/api/v2.0.0",
        "paths": {
            "/status": {"get": {"responses": {"200": {"description": "ok"}}}},
        },
        "definitions": {},
    }
    if extra_op:
        doc["paths"]["/shiny_new"] = {"get": {"responses": {"200": {"description": "ok"}}}}
    return json.dumps(doc).encode()


def _portal(
    versions: dict[str, bytes], broken: "set[str] | frozenset[str]" = frozenset()
) -> PortalClient:
    listing = "".join(
        f'<li><a href="{MEDIA}/mir_rest_api_{v}.json">MiR robot REST API {v}</a></li>'
        for v in versions
    )

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/umbraco/surface/user/LoginWebsite":
            # the real portal 302s to returnUrl on success
            return httpx.Response(302, headers={"location": FILES_PAGE})
        if path == FILES_PAGE:
            return httpx.Response(200, text=f"<html><ul>{listing}</ul></html>")
        for v, payload in versions.items():
            if path == f"{MEDIA}/mir_rest_api_{v}.json":
                if v in broken:
                    return httpx.Response(200, content=b"\x00\x01 not a spec")
                return httpx.Response(200, content=payload)
        return httpx.Response(404, text="nope")

    return PortalClient("t@example.com", "pw", transport=httpx.MockTransport(handler))


@pytest.fixture
def specs_dir(tmp_path: Path) -> Path:
    d = tmp_path / "specs"
    d.mkdir()
    (d / "registry.json").write_text(json.dumps({"tracked": [], "wanted": [], "notes": ""}) + "\n")
    return d


def _registry(specs_dir: Path) -> dict:
    return json.loads((specs_dir / "registry.json").read_text())


def test_fresh_sync_tracks_selection(specs_dir):
    versions = {"3.2.1": _swagger("3.2.1"), "3.1.0": _swagger("3.1.0"), "2.9.9": _swagger("2.9.9")}
    changed, summary = sync(specs_dir, 3, dry_run=False, client=_portal(versions))
    assert changed
    tracked = {t["mir_version"] for t in _registry(specs_dir)["tracked"]}
    assert tracked == {"3.2.1", "2.9.9", "3.1.0"}
    for v in tracked:
        assert (specs_dir / v / "swagger.json").is_file()
    assert "latest 3.2.1" in summary


def test_resync_is_idempotent(specs_dir):
    versions = {"3.2.1": _swagger("3.2.1")}
    sync(specs_dir, 3, dry_run=False, client=_portal(versions))
    changed, summary = sync(specs_dir, 3, dry_run=False, client=_portal(versions))
    assert not changed
    assert "no spec changes" in summary


def test_pinned_entries_survive_and_win(specs_dir):
    registry = _registry(specs_dir)
    registry["tracked"] = [
        {
            "mir_version": "3.2.1",
            "format": "swagger-2.0",
            "file": "3.2.1/swagger.json",
            "sha256": "x",
            "official": True,
            "pinned": True,
            "provenance": "oracle",
        }
    ]
    (specs_dir / "registry.json").write_text(json.dumps(registry))
    (specs_dir / "3.2.1").mkdir()
    (specs_dir / "3.2.1" / "swagger.json").write_bytes(_swagger("3.2.1"))

    _changed, _ = sync(
        specs_dir, 3, dry_run=False, client=_portal({"3.2.1": _swagger("3.2.1", extra_op=True)})
    )
    entry = next(t for t in _registry(specs_dir)["tracked"] if t["mir_version"] == "3.2.1")
    assert entry["pinned"] and entry["sha256"] == "x", "pinned entry must not be overwritten"


def test_superseded_patch_dir_is_removed(specs_dir):
    sync(specs_dir, 1, dry_run=False, client=_portal({"3.0.0": _swagger("3.0.0")}))
    assert (specs_dir / "3.0.0").is_dir()
    changed, _ = sync(specs_dir, 1, dry_run=False, client=_portal({"3.0.1": _swagger("3.0.1")}))
    assert changed
    assert not (specs_dir / "3.0.0").exists(), "superseded patch dir should be pruned"
    assert (specs_dir / "3.0.1" / "swagger.json").is_file()


def test_tracked_minor_line_survives_newer_minors(specs_dir):
    """Once tracked, a minor line is never rotated out by newer minor lines."""
    sync(specs_dir, 2, dry_run=False, client=_portal({"3.1.0": _swagger("3.1.0")}))
    versions = {f"3.{m}.0": _swagger(f"3.{m}.0") for m in (1, 2, 3, 4)}
    changed, _ = sync(specs_dir, 2, dry_run=False, client=_portal(versions))
    assert changed
    tracked = {t["mir_version"] for t in _registry(specs_dir)["tracked"]}
    assert tracked == {"3.4.0", "3.3.0", "3.1.0"}, "3.1 line must not be dropped"
    assert (specs_dir / "3.1.0" / "swagger.json").is_file()


def test_tracked_line_kept_when_portal_stops_publishing_it(specs_dir):
    sync(specs_dir, 1, dry_run=False, client=_portal({"3.0.0": _swagger("3.0.0")}))
    changed, summary = sync(
        specs_dir, 1, dry_run=False, client=_portal({"4.0.0": _swagger("4.0.0")})
    )
    assert changed
    tracked = {t["mir_version"] for t in _registry(specs_dir)["tracked"]}
    assert tracked == {"4.0.0", "3.0.0"}
    assert (specs_dir / "3.0.0" / "swagger.json").is_file()
    assert "kept 3.0.0" in summary


def test_tracked_line_still_gets_patch_updates_when_beyond_cap(specs_dir):
    """An old line beyond the newest-N window keeps receiving its patches."""
    sync(specs_dir, 1, dry_run=False, client=_portal({"3.1.0": _swagger("3.1.0")}))
    versions = {"3.2.0": _swagger("3.2.0"), "3.1.1": _swagger("3.1.1")}
    changed, _ = sync(specs_dir, 1, dry_run=False, client=_portal(versions))
    assert changed
    tracked = {t["mir_version"] for t in _registry(specs_dir)["tracked"]}
    assert tracked == {"3.2.0", "3.1.1"}, "old line updates to its newest patch"
    assert not (specs_dir / "3.1.0").exists(), "superseded patch dir should be pruned"
    assert (specs_dir / "3.1.1" / "swagger.json").is_file()


def test_broken_file_keeps_previous_and_continues(specs_dir):
    sync(specs_dir, 2, dry_run=False, client=_portal({"3.0.0": _swagger("3.0.0")}))
    good = (specs_dir / "3.0.0" / "swagger.json").read_bytes()

    versions = {"3.0.1": _swagger("3.0.1"), "2.5.0": _swagger("2.5.0")}
    _changed, summary = sync(
        specs_dir, 2, dry_run=False, client=_portal(versions, broken={"3.0.1"})
    )
    assert "kept previous spec for 3.0.1; error" in summary
    # the healthy version still landed
    assert (specs_dir / "2.5.0" / "swagger.json").is_file()
    # and the broken one did not clobber anything
    assert not (specs_dir / "3.0.1").exists()
    assert (specs_dir / "3.0.0" / "swagger.json").read_bytes() == good


def test_force_reconverts_unchanged_sources(specs_dir):
    versions = {"3.2.1": _swagger("3.2.1")}
    sync(specs_dir, 3, dry_run=False, client=_portal(versions))
    changed, _ = sync(specs_dir, 3, dry_run=False, force=True, client=_portal(versions))
    assert changed  # re-processed even though source_sha256 matched


def test_report_contains_api_diff(specs_dir, tmp_path):
    sync(specs_dir, 1, dry_run=False, client=_portal({"3.0.0": _swagger("3.0.0")}))
    report = tmp_path / "report.md"
    sync(
        specs_dir,
        1,
        dry_run=False,
        client=_portal({"3.1.0": _swagger("3.1.0", extra_op=True)}),
        report_path=report,
    )
    text = report.read_text()
    assert "API changes 3.0.0 → 3.1.0" in text
    assert "`GET /shiny_new`" in text


def test_report_gets_ai_summary_when_configured(specs_dir, tmp_path):
    sync(specs_dir, 1, dry_run=False, client=_portal({"3.0.0": _swagger("3.0.0")}))
    report = tmp_path / "report.md"
    sync(
        specs_dir,
        1,
        dry_run=False,
        client=_portal({"3.1.0": _swagger("3.1.0", extra_op=True)}),
        report_path=report,
        summarizer=lambda md: "Integrators gain `GET /shiny_new`.",
    )
    text = report.read_text()
    assert text.index("Release impact (AI-generated)") < text.index("API changes")
    assert "Integrators gain" in text


def test_ai_summary_failure_never_blocks_the_sync(specs_dir, tmp_path):
    from mir_spec_scraper.summarize import SummaryError

    def broken(_md: str) -> str:
        raise SummaryError("OpenRouter request failed (ConnectError)")

    sync(specs_dir, 1, dry_run=False, client=_portal({"3.0.0": _swagger("3.0.0")}))
    report = tmp_path / "report.md"
    changed, summary = sync(
        specs_dir,
        1,
        dry_run=False,
        client=_portal({"3.1.0": _swagger("3.1.0", extra_op=True)}),
        report_path=report,
        summarizer=broken,
    )
    assert changed  # the spec update still happened
    assert "AI summary skipped" in summary
    text = report.read_text()
    assert "API changes 3.0.0 → 3.1.0" in text  # mechanical report still written
    assert "Release impact" not in text


def test_dry_run_writes_nothing(specs_dir):
    changed, _ = sync(specs_dir, 3, dry_run=True, client=_portal({"3.2.1": _swagger("3.2.1")}))
    assert changed
    assert not (specs_dir / "3.2.1").exists()
    assert _registry(specs_dir)["tracked"] == []


def test_missing_credentials_is_graceful(specs_dir, monkeypatch):
    monkeypatch.delenv("MIR_PORTAL_EMAIL", raising=False)
    monkeypatch.delenv("MIR_PORTAL_PASSWORD", raising=False)
    changed, summary = sync(specs_dir, 3, dry_run=False)
    assert not changed
    assert "skipped" in summary


def test_portal_base_is_https():
    assert PORTAL_BASE.startswith("https://")
