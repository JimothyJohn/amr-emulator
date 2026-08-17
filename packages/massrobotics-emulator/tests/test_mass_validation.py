"""Schema/validation unit tests, including the vendored upstream quirks."""

import hashlib
import json
from importlib import resources

from massrobotics_emulator import AMRConfig, MassRoboticsAMR, validation_errors, vecna_config
from massrobotics_emulator.validation import ProtocolViolation, validate_outgoing


def test_vendored_schema_hash_matches_registry():
    root = resources.files("massrobotics_emulator.schemas")
    raw = (root / "AMR_Interop_Standard.json").read_bytes()
    registry = json.loads((root / "registry.json").read_text())
    assert hashlib.sha256(raw).hexdigest() == registry["source"]["vendored_sha256"]
    assert registry["source"]["normalizations"] == []


def test_identity_report_is_schema_valid():
    for model in ("APT", "ATG", "AFL", "CPJ"):
        robot = MassRoboticsAMR(vecna_config(model))
        assert validation_errors(robot.identity_report(), "identityReport") == []
        # and against the root oneOf, exactly as the reference receiver checks
        assert validation_errors(robot.identity_report()) == []


def test_status_report_is_schema_valid_idle_and_navigating():
    robot = MassRoboticsAMR(vecna_config("APT"))
    assert validation_errors(robot.status_report(), "statusReport") == []
    robot.navigate_to(10.0, 5.0)
    report = robot.status_report()
    assert validation_errors(report, "statusReport") == []
    assert report["operationalState"] == "navigating"
    assert report["destinations"][0]["planarDatumUUID"]
    assert 1 <= len(report["path"]) <= 10


def test_error_codes_present_only_when_erroring():
    robot = MassRoboticsAMR(vecna_config("CPJ"))
    assert "errorCodes" not in robot.status_report()
    robot.set_error("E-STOP")
    report = robot.status_report()
    assert report["errorCodes"] == ["E-STOP"]
    assert report["operationalState"] == "disabled"
    assert validation_errors(report, "statusReport") == []


def test_uuid_is_lowercase_and_deterministic():
    # The schema's uuid pattern accepts lowercase hex only — the upstream
    # examples use uppercase and fail their own schema (registry.json note).
    config = vecna_config("ATG", serial_number="ATG-0042")
    assert config.uuid == config.uuid.lower()
    assert config.uuid == vecna_config("ATG", serial_number="ATG-0042").uuid
    assert config.uuid != vecna_config("ATG", serial_number="ATG-0043").uuid


def test_upstream_example_uppercase_uuid_fails_schema():
    robot = MassRoboticsAMR(AMRConfig())
    report = robot.identity_report()
    report["uuid"] = report["uuid"].upper()
    assert any("uuid" in problem for problem in validation_errors(report, "identityReport"))


def test_validate_outgoing_raises_with_specific_problems():
    robot = MassRoboticsAMR(AMRConfig())
    report = robot.status_report()
    del report["location"]["angle"]  # required by the schema's location def
    try:
        validate_outgoing(report, "statusReport")
    except ProtocolViolation as violation:
        assert any("angle" in problem for problem in violation.problems)
    else:
        raise AssertionError("schema-invalid statusReport was not rejected")


def test_root_oneof_rejects_hybrid_message():
    robot = MassRoboticsAMR(AMRConfig())
    hybrid = {**robot.identity_report(), **robot.status_report()}
    assert validation_errors(hybrid) != []
