"""Guards that keep the scraper safe against a hostile or drifted portal."""

import pytest
from amr_spec_scraper.pdf_convert import _consistency_warnings, parse_schema_token
from amr_spec_scraper.portal import PortalClient, PortalFile


def _client() -> PortalClient:
    return PortalClient("user@example.com", "hunter2")


@pytest.mark.parametrize(
    "url",
    [
        "http://supportportal.mobile-industrial-robots.com/f.pdf",  # not https
        "https://evil.example.com/f.pdf",  # foreign host
        "ftp://supportportal.mobile-industrial-robots.com/f.pdf",
        "https://supportportal.mobile-industrial-robots.com.evil.example/f.pdf",
    ],
)
def test_download_refuses_offsite_urls(url):
    client = _client()
    try:
        with pytest.raises(ValueError, match="refusing to download"):
            client.download(PortalFile(version=(9, 9, 9), url=url, label="x"))
    finally:
        client.close()


def test_unknown_schema_notation_degrades_with_marker():
    token = parse_schema_token("< GetX > set")  # hypothetical future notation
    assert token == {"type": "object", "x-mir-unparsed": "<GetX>set"}


def test_consistency_warnings_flag_unparsed_and_dangling():
    doc = {
        "paths": {
            "/a": {
                "get": {
                    "responses": {
                        "200": {"schema": {"type": "object", "x-mir-unparsed": "<GetX>set"}}
                    }
                }
            }
        },
        "definitions": {
            "A": {"type": "object", "properties": {"b": {"$ref": "#/definitions/Missing"}}}
        },
    }
    warnings = _consistency_warnings(doc)
    assert any("unrecognized schema notation" in w for w in warnings)
    assert any("dangling $ref to undefined 'Missing'" in w for w in warnings)
    # the marker must not leak into the shipped document
    assert "x-mir-unparsed" not in str(doc["paths"])
