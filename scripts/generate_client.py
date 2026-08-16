"""Regenerate the mir-client SDK from the bundled official specs.

    uv run python scripts/generate_client.py [--check]

Reads the spec registry, converts the newest robot swagger to OpenAPI 3, and
runs openapi-python-client for the robot API and the Fleet Integration API
into packages/mir-client/src/mir_client/{robot,fleet}. Those two directories
are ENTIRELY generated — never hand-edit them; edit the specs pipeline or this
script instead. Hand-written files (pyproject, __init__, auth.py) live outside
them. `--check` regenerates into a temp dir and exits 1 on drift, which is how
CI proves the committed SDK matches the registry.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLIENT_SRC = REPO / "packages" / "mir-client" / "src" / "mir_client"


def _generate(spec_path: Path, package: str, out_dir: Path, extra_config: str = "") -> None:
    generator = shutil.which("openapi-python-client")
    if generator is None:
        raise RuntimeError("openapi-python-client not installed (uv sync --all-packages)")
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as config:
        config.write(f"package_name_override: {package}\n")
        config.write(f"project_name_override: mir-client-{package}\n")
        # --isolated pins the generator's ruff post-processing to default
        # rules regardless of where the output lands; otherwise generating
        # into the repo picks up our config and into /tmp does not, and the
        # drift check can never pass.
        config.write("post_hooks:\n")
        # --select pins the exact rule set: ruff's --isolated defaults have
        # changed across minor versions (0.16 started flagging generated
        # docstrings), and the drift check needs generator output to be
        # stable under ruff upgrades.
        config.write(
            '  - "ruff check . --fix --isolated --select E4,E7,E9,F,I --line-length 100"\n'
        )
        config.write('  - "ruff format . --isolated --line-length 100"\n')
        config.write(extra_config)
        config_path = config.name
    subprocess.run(  # noqa: S603 - fixed args; dev-group console script
        [
            generator,
            "generate",
            "--path",
            str(spec_path),
            "--meta",
            "none",
            "--config",
            config_path,
            "--output-path",
            str(out_dir),
            "--overwrite",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    shutil.rmtree(out_dir / ".ruff_cache", ignore_errors=True)


def _norm(name: str) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", name).lower()


def _inline_child_names(schemas: dict) -> set[str]:
    """Normalized names of the models the generator will synthesize for
    inline object properties (recursively: Parent + prop [+ prop...])."""
    names: set[str] = set()

    def walk(prefix: str, schema: dict) -> None:
        for prop, sub in (schema.get("properties") or {}).items():
            if isinstance(sub, dict) and (sub.get("type") == "object" or "properties" in sub):
                child = prefix + prop
                names.add(_norm(child))
                walk(child, sub)

    for name, schema in schemas.items():
        if isinstance(schema, dict):
            walk(name, schema)
    return names


def _rename_colliding_schemas(doc: dict) -> None:
    """Rename top-level schemas whose generated class name would collide with
    a synthesized inline-property model (e.g. GetHook_brake vs GetHook's
    inline `brake` object → both become GetHookBrake and the generator drops
    both, plus every response referencing them)."""
    schemas = doc.get("components", {}).get("schemas", {})
    children = _inline_child_names(schemas)
    for name in list(schemas):
        if _norm(name) in children:
            replacement = name + "_document"
            while _norm(replacement) in children or replacement in schemas:
                replacement += "_x"
            _rename_schema(doc, name, replacement)


def _rename_schema(doc: dict, old: str, new: str) -> None:
    """Rename a component schema and rewrite every $ref to it."""
    schemas = doc.get("components", {}).get("schemas", {})
    if old not in schemas:
        return
    schemas[new] = schemas.pop(old)
    old_ref, new_ref = f"#/components/schemas/{old}", f"#/components/schemas/{new}"

    def rewrite(node: object) -> None:
        if isinstance(node, dict):
            if node.get("$ref") == old_ref:
                node["$ref"] = new_ref
            for value in node.values():
                rewrite(value)
        elif isinstance(node, list):
            for value in node:
                rewrite(value)

    rewrite(doc)


def _strip_deprecated_properties(node: object) -> None:
    """Remove schema properties marked deprecated, in place.

    The Fleet specs keep deprecated camelCase aliases (readOnly+deprecated)
    beside their kebab-case replacements; the generator's collision handling
    produces invalid identifiers for the pair (field_pallet-length). A fresh
    client has no business exposing deprecated aliases, so drop them.
    """
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict):
            for name in [
                n
                for n, s in properties.items()
                if isinstance(s, dict) and s.get("deprecated") is True
            ]:
                del properties[name]
        for value in node.values():
            _strip_deprecated_properties(value)
    elif isinstance(node, list):
        for value in node:
            _strip_deprecated_properties(value)


def generate_into(base: Path) -> dict:
    """Generate both clients under *base*; return provenance details."""
    from mir_emulator import registry
    from mir_emulator.openapi3 import to_openapi3
    from mir_emulator.spec import load_spec

    robot_version, robot_path = registry.spec_path()
    fleet_version, fleet_path = registry.fleet_spec_path()

    robot_doc = to_openapi3(load_spec(robot_path, robot_version).document)
    _rename_colliding_schemas(robot_doc)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump(robot_doc, tmp)
        robot_oas3 = Path(tmp.name)

    fleet_doc = json.loads(fleet_path.read_text())
    _strip_deprecated_properties(fleet_doc)
    _rename_colliding_schemas(fleet_doc)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump(fleet_doc, tmp)
        fleet_stripped = Path(tmp.name)

    _generate(robot_oas3, "robot", base / "robot")
    _generate(fleet_stripped, "fleet", base / "fleet")

    provenance = {
        "robot_version": robot_version,
        "robot_spec_sha256": registry.tracked_entry(robot_version)["sha256"],
        "fleet_version": fleet_version,
        "fleet_spec_sha256": registry.fleet_tracked_entry(fleet_version)["sha256"],
    }
    (base / "_provenance.py").write_text(
        '"""Generated by scripts/generate_client.py — DO NOT EDIT."""\n\n'
        + "".join(f'{k.upper()} = "{v}"\n' for k, v in provenance.items())
    )
    return provenance


def _tree_differs(a: Path, b: Path) -> list[str]:
    diffs: list[str] = []
    compare = filecmp.dircmp(a, b)

    def walk(cmp: filecmp.dircmp, prefix: str) -> None:
        for name in (*cmp.left_only, *cmp.right_only, *cmp.diff_files, *cmp.funny_files):
            diffs.append(prefix + name)
        for sub_name, sub in cmp.subdirs.items():
            walk(sub, f"{prefix}{sub_name}/")

    walk(compare, "")
    return diffs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate into a temp dir and fail on drift against the committed SDK",
    )
    args = parser.parse_args()

    if not args.check:
        provenance = generate_into(CLIENT_SRC)
        print(f"generated mir_client from {provenance}")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp)
        generate_into(fresh)
        diffs: list[str] = []
        for part in ("robot", "fleet", "_provenance.py"):
            committed, regenerated = CLIENT_SRC / part, fresh / part
            if regenerated.is_file():
                if not committed.is_file() or committed.read_text() != regenerated.read_text():
                    diffs.append(part)
            elif not committed.is_dir():
                diffs.append(part)
            else:
                diffs.extend(f"{part}/{d}" for d in _tree_differs(committed, regenerated))
        if diffs:
            print("mir-client has drifted from the registry; regenerate with:")
            print("    uv run python scripts/generate_client.py")
            for d in diffs[:20]:
                print(f"  differs: {d}")
            return 1
        print("mir-client matches the registry")
        return 0


if __name__ == "__main__":
    sys.exit(main())
