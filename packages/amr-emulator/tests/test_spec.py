"""Invariants every bundled spec must satisfy after normalization."""

import pytest
from amr_emulator import registry
from amr_emulator.spec import load_spec


@pytest.fixture(params=registry.supported_versions())
def spec(request):
    version, path = registry.spec_path(request.param)
    return load_spec(path, version)


def test_base_path_is_v2(spec):
    assert spec.base_path == "/api/v2.0.0"


def test_has_substantial_surface(spec):
    assert len(spec.operations) > 150


def test_core_endpoints_present(spec):
    for key in [("GET", "/status"), ("GET", "/missions"), ("POST", "/mission_queue")]:
        assert key in spec.operations, f"{key} missing from {spec.mir_version}"


def test_every_operation_declares_a_success_status(spec):
    for op in spec.operations.values():
        assert 200 <= op.success_status < 300 or op.success_status == 200


def test_deref_terminates_on_all_response_schemas(spec):
    for op in spec.operations.values():
        for schema in op.responses.values():
            deref = spec.deref(schema)
            assert isinstance(deref, dict)


def test_unknown_version_raises():
    with pytest.raises(KeyError):
        registry.spec_path("99.99.99")


def test_registry_sha256_matches_files():
    from hashlib import sha256

    for tracked in registry.tracked_specs():
        _, path = registry.spec_path(tracked.mir_version)
        assert sha256(path.read_bytes()).hexdigest() == tracked.sha256
