import pytest
from amr_emulator import auth, registry
from amr_emulator.app import create_app
from amr_emulator.spec import load_spec
from starlette.testclient import TestClient

ALL_VERSIONS = registry.supported_versions()

AUTH_HEADER = {"Authorization": f"Basic {auth.expected_token('distributor', 'distributor')}"}


@pytest.fixture(params=ALL_VERSIONS, scope="module")
def mir_version(request):
    return request.param


@pytest.fixture(scope="module")
def spec(mir_version):
    version, path = registry.spec_path(mir_version)
    return load_spec(path, version)


@pytest.fixture(scope="module")
def client(mir_version):
    app = create_app(mir_version)
    with TestClient(app, base_url="http://emulator.test") as test_client:
        yield test_client
