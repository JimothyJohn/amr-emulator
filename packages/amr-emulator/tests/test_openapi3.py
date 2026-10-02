"""OpenAPI 3 conversion is validated by round-trip: the emulator's own OA3
loader must reconstruct the identical operation table from the converted doc."""

import json

import pytest
from amr_emulator import registry
from amr_emulator.openapi3 import to_openapi3
from amr_emulator.spec import load_spec


@pytest.fixture(params=registry.supported_versions())
def swagger_spec(request):
    version, path = registry.spec_path(request.param)
    spec = load_spec(path, version)
    if spec.document.get("swagger") != "2.0":
        pytest.skip("only swagger-2.0 sources are converted")
    return spec


def test_round_trip_preserves_operations(swagger_spec, tmp_path):
    converted = to_openapi3(swagger_spec.document)
    out = tmp_path / "openapi3.json"
    out.write_text(json.dumps(converted))
    reloaded = load_spec(out, swagger_spec.mir_version)

    assert reloaded.base_path == swagger_spec.base_path
    assert set(reloaded.operations) == set(swagger_spec.operations)
    for key, op in swagger_spec.operations.items():
        other = reloaded.operations[key]
        assert other.success_status == op.success_status, key
        assert set(other.responses) == set(op.responses), key
        assert (other.body_schema is None) == (op.body_schema is None), key
        assert other.path_param_types() == op.path_param_types(), key


def test_no_swagger2_ref_prefixes_survive(swagger_spec):
    converted = json.dumps(to_openapi3(swagger_spec.document))
    assert "#/definitions/" not in converted
    assert converted.count("#/components/schemas/") > 0


def test_rejects_non_swagger2():
    with pytest.raises(ValueError):
        to_openapi3({"openapi": "3.0.3"})
