"""Runtime version-diff surface: the upgrade-preflight for integrators.

The load-bearing invariant is the converter oracle, made user-visible: the
pinned official 3.5.4 and the PDF-converted 3.5.6 must diff structurally
clean, or the endpoint would report the conversion pipeline's information
loss as API changes.
"""

import pytest
from amr_emulator import registry
from amr_emulator.diff import diff_versions, schema_signature


def test_oracle_invariant_pinned_354_vs_converted_356_is_clean():
    diff = diff_versions("3.5.4", "3.5.6")
    assert diff["structurally_identical"], diff


def test_cross_generation_diff_reports_real_changes():
    diff = diff_versions("2.14.7", "3.8.1")
    assert not diff["structurally_identical"]
    assert diff["family"] == "robot"
    assert diff["operations"]["added"], "3.x adds operations over 2.x"
    assert diff["operations"]["removed"], "3.x drops operations from 2.x"
    assert all(" " in entry for entry in diff["operations"]["added"])  # "METHOD /path"


def test_diff_is_directional():
    forward = diff_versions("2.14.7", "3.8.1")
    backward = diff_versions("3.8.1", "2.14.7")
    assert forward["operations"]["added"] == backward["operations"]["removed"]
    assert forward["operations"]["removed"] == backward["operations"]["added"]


def test_self_diff_is_identical_for_every_tracked_version():
    for version in [*registry.supported_versions(), *registry.fleet_supported_versions()]:
        diff = diff_versions(version, version)
        assert diff["structurally_identical"], version


def test_fleet_diff_shows_the_robots_endpoint_arriving():
    diff = diff_versions("1.3.1", "1.5.0")
    assert diff["family"] == "fleet"
    assert "GET /api/v1/robots" in diff["operations"]["added"]


def test_cross_family_diff_is_refused():
    with pytest.raises(ValueError, match="family"):
        diff_versions("3.8.1", "1.5.0")


def test_unknown_version_raises_with_the_available_list():
    with pytest.raises(KeyError, match="not tracked"):
        diff_versions("9.9.9", "3.8.1")


def test_schema_signature_ignores_descriptions_and_pdf_lossy_keys():
    rich = {
        "type": "object",
        "description": "prose",
        "required": ["a"],
        "properties": {"a": {"type": "string", "minLength": 1, "description": "x"}},
        "additionalProperties": False,
    }
    lossy = {"type": "object", "properties": {"a": {"type": "string"}}}
    assert schema_signature(rich) == schema_signature(lossy)


def test_schema_signature_catches_type_and_property_changes():
    a = {"type": "object", "properties": {"a": {"type": "string"}}}
    assert schema_signature(a) != schema_signature(
        {"type": "object", "properties": {"a": {"type": "integer"}}}
    )
    assert schema_signature(a) != schema_signature(
        {"type": "object", "properties": {"b": {"type": "string"}}}
    )
