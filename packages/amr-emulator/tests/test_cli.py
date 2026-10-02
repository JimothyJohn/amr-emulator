"""CLI wiring: export modes, flags reaching the app, and pipe behavior.

The serve path itself (uvicorn over TCP) is covered by tests/test_integration.py;
here we stop at the uvicorn.run boundary and assert the app it would serve.
"""

import json
import subprocess
import sys

import pytest
import uvicorn
from amr_emulator import auth, registry
from amr_emulator.cli import build_parser, main
from starlette.testclient import TestClient

DEFAULT_AUTH = {
    "Authorization": f"Basic {auth.expected_token(auth.DEFAULT_USERNAME, auth.DEFAULT_PASSWORD)}"
}


def test_export_swagger2_prints_the_bundled_document(capsys):
    assert main(["--export", "swagger2"]) == 0
    doc = json.loads(capsys.readouterr().out)
    _version, path = registry.spec_path(None)
    assert doc == json.loads(path.read_text())
    assert doc["swagger"] == "2.0"


def test_export_openapi3_converts_the_document(capsys):
    assert main(["--export", "openapi3"]) == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["openapi"].startswith("3.")
    assert "swagger" not in doc


def test_export_respects_mir_version(capsys):
    oldest = registry.supported_versions()[-1]
    assert main(["--mir-version", oldest, "--export", "swagger2"]) == 0
    doc = json.loads(capsys.readouterr().out)
    _version, path = registry.spec_path(oldest)
    assert doc == json.loads(path.read_text())


def test_unknown_mir_version_names_the_available_ones():
    with pytest.raises(KeyError, match="not tracked"):
        main(["--mir-version", "9.9.9", "--export", "swagger2"])


def test_invalid_export_format_is_rejected(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--export", "graphql"])
    assert exc_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.startswith("amr-emulator ")


def test_env_vars_feed_credential_defaults(monkeypatch):
    monkeypatch.setenv("AMR_EMULATOR_USERNAME", "alice")
    monkeypatch.setenv("AMR_EMULATOR_PASSWORD", "s3cret")
    args = build_parser().parse_args([])
    assert (args.username, args.password) == ("alice", "s3cret")


@pytest.fixture
def served_app(monkeypatch):
    """Run main() up to the uvicorn.run boundary and capture what it would serve."""
    captured = {}

    def fake_run(app, **kwargs):
        captured["app"] = app
        captured.update(kwargs)

    monkeypatch.setattr(uvicorn, "run", fake_run)

    def serve(argv):
        assert main(argv) == 0
        return captured

    return serve


def test_default_serve_enforces_auth(served_app, capsys):
    captured = served_app([])
    assert (captured["host"], captured["port"]) == ("127.0.0.1", 8080)
    banner = capsys.readouterr().out
    assert "http://127.0.0.1:8080/api/v2.0.0" in banner
    assert "auth:" in banner
    with TestClient(captured["app"]) as client:
        assert client.get("/api/v2.0.0/status").status_code == 401
        assert client.get("/api/v2.0.0/status", headers=DEFAULT_AUTH).status_code == 200


def test_no_auth_flag_disables_auth(served_app, capsys):
    captured = served_app(["--no-auth", "--host", "127.0.0.2", "--port", "9090"])
    assert (captured["host"], captured["port"]) == ("127.0.0.2", 9090)
    assert "auth:" not in capsys.readouterr().out
    with TestClient(captured["app"]) as client:
        assert client.get("/api/v2.0.0/status").status_code == 200


def test_credential_flags_replace_the_default_account(served_app):
    captured = served_app(["--username", "alice", "--password", "s3cret"])
    alice = {"Authorization": f"Basic {auth.expected_token('alice', 's3cret')}"}
    with TestClient(captured["app"]) as client:
        assert client.get("/api/v2.0.0/status", headers=alice).status_code == 200
        assert client.get("/api/v2.0.0/status", headers=DEFAULT_AUTH).status_code == 401


def test_cors_flag_controls_cross_origin_access(served_app):
    origin = {"Origin": "http://dashboard.example"}
    with TestClient(served_app(["--cors"])["app"]) as client:
        response = client.get("/api/v2.0.0/status", headers={**DEFAULT_AUTH, **origin})
        assert response.headers.get("access-control-allow-origin")
    with TestClient(served_app([])["app"]) as client:
        response = client.get("/api/v2.0.0/status", headers={**DEFAULT_AUTH, **origin})
        assert "access-control-allow-origin" not in response.headers


def test_export_survives_the_reader_hanging_up():
    """`amr-emulator --export swagger2 | head` must exit 0, not spew EPIPE."""
    script = "from amr_emulator.cli import main; raise SystemExit(main(['--export', 'swagger2']))"
    proc = subprocess.Popen(  # noqa: S603 - fixed argv, our own interpreter
        [sys.executable, "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None and proc.stderr is not None
    proc.stdout.read(64)
    proc.stdout.close()  # reader hangs up mid-stream -> EPIPE in the child
    stderr = proc.stderr.read().decode(errors="replace")
    assert proc.wait(timeout=30) == 0, stderr
    assert "Traceback" not in stderr
