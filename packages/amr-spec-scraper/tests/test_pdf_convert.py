"""Converter cell-parsing units + the live oracle test.

The oracle: converting the official 3.5.4 PDF must be structurally identical
to MiR's official 3.5.4 swagger.json (bundled, pinned). It needs portal
credentials to fetch the PDF, so it runs with the live_portal marker (weekly
in scrape.yml, or locally with .env loaded).
"""

import os

import pytest
from amr_spec_scraper.pdf_convert import (
    _front_matter,
    parse_name_cell,
    parse_schema_token,
)


def test_name_cell_unwraps_and_strips_flags():
    assert parse_name_cell("Authorizatio\nn\nrequired") == ("Authorization", True)
    assert parse_name_cell("cart_calibrati\non\noptional") == ("cart_calibration", False)
    assert parse_name_cell("guid") == ("guid", False)
    assert parse_name_cell(None) == ("", False)
    assert parse_name_cell("required") == ("", True)


def test_schema_token_basics():
    assert parse_schema_token("string") == {"type": "string"}
    assert parse_schema_token("string (date-\ntime)") == {"type": "string", "format": "date-time"}
    assert parse_schema_token("integer (int32)") == {"type": "integer", "format": "int32"}
    assert parse_schema_token("number (float)") == {"type": "number", "format": "float"}
    assert parse_schema_token("boolean") == {"type": "boolean"}
    assert parse_schema_token("No Content") is None
    assert parse_schema_token("") is None
    assert parse_schema_token(None) is None


def test_schema_token_refs_arrays_enums():
    assert parse_schema_token("PostCart_calibratio\nns") == {
        "$ref": "#/definitions/PostCart_calibrations"
    }
    assert parse_schema_token("< GetMissions >\narray") == {
        "type": "array",
        "items": {"$ref": "#/definitions/GetMissions"},
    }
    assert parse_schema_token("< object > array") == {
        "type": "array",
        "items": {"type": "object"},
    }
    assert parse_schema_token("enum (en_US,\nde_DE, es_ES)") == {
        "type": "string",
        "enum": ["en_US", "de_DE", "es_ES"],
    }
    assert parse_schema_token("< string, object >\nmap") == {
        "type": "object",
        "additionalProperties": {"type": "object"},
    }


def test_front_matter_new_style():
    text = "3.8.1 MIR250 REST API\nOverview\nVersion : 3.8.1\nBasePath : /api/v2.0.0\n"
    assert _front_matter(text) == ("3.8.1 MIR250 REST API", "3.8.1", "/api/v2.0.0")


def test_front_matter_old_style_folds_host_path():
    text = (
        "2.14.7 MIR250 REST API\nOverview\nVersion : 2.14.7\n"
        "Host : mir.com/api\nBasePath : /v2.0.0\n"
    )
    assert _front_matter(text) == ("2.14.7 MIR250 REST API", "2.14.7", "/api/v2.0.0")


def test_front_matter_version_falls_back_to_title():
    assert _front_matter("2.14.7 MIR250 REST API\n")[1] == "2.14.7"


def test_excerpt_pdf_converts_offline():
    """3 real pages of the official 3.5.4 PDF (cover, one operation, start of
    Definitions) committed as a fixture — offline regression for the parsing
    core. The full-document oracle runs live (below)."""
    from pathlib import Path

    from amr_spec_scraper.pdf_convert import convert_pdf

    fixture = Path(__file__).parent / "fixtures" / "mir_354_excerpt.pdf"
    doc = convert_pdf(str(fixture))

    assert doc["info"]["version"] == "3.5.4"
    assert doc["basePath"] == "/api/v2.0.0"
    op = doc["paths"]["/cart_calibrations"]["post"]
    body = next(p for p in op["parameters"] if p["in"] == "body")
    assert body["schema"] == {"$ref": "#/definitions/PostCart_calibrations"}
    assert set(op["responses"]) == {"201", "400", "409"}
    assert op["responses"]["201"]["schema"] == {"$ref": "#/definitions/GetCart_calibrations"}

    error = doc["definitions"]["Error"]
    assert set(error["properties"]) == {"error_code", "error_human"}
    assert error["properties"]["error_code"]["type"] == "string"
    # dangling refs are expected (we only kept 3 pages) and must be *flagged*
    assert any("dangling" in w for w in doc.get("x-mir-converter-warnings", []))


@pytest.mark.live_portal
@pytest.mark.skipif(
    not os.environ.get("MIR_PORTAL_EMAIL"),
    reason="needs MIR_PORTAL_EMAIL/MIR_PORTAL_PASSWORD",
)
def test_oracle_pdf_conversion_matches_official_swagger(tmp_path):
    """Regression gate for the whole PDF->swagger pipeline."""
    import json

    from amr_emulator import registry
    from amr_spec_scraper.pdf_convert import convert_pdf
    from amr_spec_scraper.portal import PortalClient
    from amr_spec_scraper.validate import compare

    client = PortalClient(os.environ["MIR_PORTAL_EMAIL"], os.environ["MIR_PORTAL_PASSWORD"])
    try:
        client.login()
        payload = client._http.get(
            "https://supportportal.mobile-industrial-robots.com/"
            "support-files/manuals/PDF/rest_api/MiR_MIR250_REST_API_3.5.4.pdf"
        ).content
    finally:
        client.close()
    assert payload[:5] == b"%PDF-"

    pdf_path = tmp_path / "official_354.pdf"
    pdf_path.write_bytes(payload)
    converted = convert_pdf(str(pdf_path))

    _version, official_path = registry.spec_path("3.5.4")
    official = json.loads(official_path.read_text())

    problems = compare(converted, official)
    assert not problems, "\n".join(problems[:20])
