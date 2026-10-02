"""The CLI entry point: exit codes and the $GITHUB_OUTPUT contract.

$GITHUB_OUTPUT is line-oriented key=value; the summary contains portal-derived
text (URLs, labels, error messages), so a newline smuggled through it could
forge workflow outputs like changed=true. These tests pin that door shut.
"""

import json
from pathlib import Path

from amr_spec_scraper.cli import _github_output, main


def _specs_dir(tmp_path: Path) -> Path:
    d = tmp_path / "specs"
    d.mkdir()
    (d / "registry.json").write_text(json.dumps({"tracked": [], "wanted": [], "notes": ""}) + "\n")
    return d


def test_main_without_registry_exits_2(tmp_path, capsys):
    assert main(["sync", "--specs-dir", str(tmp_path)]) == 2
    assert "no registry.json" in capsys.readouterr().err


def test_main_without_credentials_is_a_clean_skip(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("MIR_PORTAL_EMAIL", raising=False)
    monkeypatch.delenv("MIR_PORTAL_PASSWORD", raising=False)
    output = tmp_path / "github_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert main(["sync", "--specs-dir", str(_specs_dir(tmp_path))]) == 0
    assert "skipped" in capsys.readouterr().out
    lines = output.read_text().splitlines()
    assert "changed=false" in lines
    assert any(line.startswith("summary=skipped") for line in lines)


def test_github_output_is_a_noop_outside_actions(monkeypatch):
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    _github_output(True, "anything")  # must not raise or write anywhere


def test_github_output_appends_both_keys(tmp_path, monkeypatch):
    output = tmp_path / "github_output"
    output.write_text("existing=1\n")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    _github_output(True, "added 3.9.0")
    assert output.read_text() == "existing=1\nchanged=true\nsummary=added 3.9.0\n"


def test_hostile_summary_cannot_forge_workflow_outputs(tmp_path, monkeypatch):
    """A portal error message containing a newline must not become an extra
    key=value line in $GITHUB_OUTPUT (e.g. flipping changed to true)."""
    output = tmp_path / "github_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    _github_output(False, "kept previous spec for 3.0.1; error: boom\nchanged=true\rsummary=pwned")
    lines = output.read_text().splitlines()
    assert [line for line in lines if line.startswith("changed=")] == ["changed=false"]
    assert len([line for line in lines if line.startswith("summary=")]) == 1
