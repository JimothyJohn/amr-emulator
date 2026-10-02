"""Portal HTML parsing (synthetic fixture) and an opt-in live-portal test.

The live test is the real integration test; it only runs when portal
credentials are present (locally or in the scheduled scrape workflow).
"""

import os
from pathlib import Path

import pytest
from amr_spec_scraper.portal import parse_file_listing

FIXTURE = (Path(__file__).parent / "fixtures" / "rest_api_files.html").read_text()


def test_fixture_listing_finds_all_versions():
    files = parse_file_listing(FIXTURE)
    versions = {f.version_str for f in files}
    assert versions == {"3.5.4", "3.4.1", "2.14.7", "2.13.3.1"}


def test_urls_are_absolute():
    for file in parse_file_listing(FIXTURE):
        assert file.url.startswith("https://")


def test_ignores_non_spec_links():
    files = parse_file_listing(FIXTURE)
    assert not any("release-note" in f.url for f in files)


def test_hostile_html_does_not_crash():
    for blob in [
        "",
        "<a href='x.json'>1.2.3</a >" * 1000,
        "<a><a><a href=>3.5.4",
        "<a href='javascript:alert(1)'>REST API 9.9.9</a>",
        "\x00<a href='/f.json'>rest api 1.2.3</a>",
        "<a href='" + "A" * 100_000 + ".json'>rest api 1.2.3</a>",
    ]:
        parse_file_listing(blob)  # must not raise


@pytest.mark.live_portal
@pytest.mark.skipif(
    not os.environ.get("MIR_PORTAL_EMAIL"),
    reason="needs MIR_PORTAL_EMAIL/MIR_PORTAL_PASSWORD",
)
def test_live_portal_listing():
    from amr_spec_scraper.portal import PortalClient

    client = PortalClient(os.environ["MIR_PORTAL_EMAIL"], os.environ["MIR_PORTAL_PASSWORD"])
    try:
        client.login()
        files = client.list_files()
    finally:
        client.close()
    assert files, "live portal listing parsed to zero files — parser needs updating"
