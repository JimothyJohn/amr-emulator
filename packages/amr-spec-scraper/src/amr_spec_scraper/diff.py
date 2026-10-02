"""Human-readable API changelog between two swagger documents.

Rendered into the scrape PR body so a new MiR release arrives with a review
map: what endpoints appeared, disappeared, or changed shape — instead of a
40k-line JSON diff.
"""

from __future__ import annotations

from amr_spec_scraper.validate import _op_signature, schema_signature


def _ops(doc: dict) -> dict[tuple[str, str], dict]:
    return {
        (method.lower(), path): op
        for path, item in doc.get("paths", {}).items()
        for method, op in item.items()
        if method.lower() in ("get", "post", "put", "delete", "patch")
    }


def api_diff_markdown(old: dict, new: dict, old_label: str, new_label: str) -> str:
    """Markdown summary of `old_label -> new_label` API changes."""
    old_ops, new_ops = _ops(old), _ops(new)
    added = sorted(set(new_ops) - set(old_ops))
    removed = sorted(set(old_ops) - set(new_ops))
    changed = sorted(
        key
        for key in set(old_ops) & set(new_ops)
        if _op_signature(old_ops[key]) != _op_signature(new_ops[key])
    )

    old_defs, new_defs = old.get("definitions", {}), new.get("definitions", {})
    defs_added = sorted(set(new_defs) - set(old_defs))
    defs_removed = sorted(set(old_defs) - set(new_defs))
    defs_changed = sorted(
        name
        for name in set(old_defs) & set(new_defs)
        if schema_signature(old_defs[name]) != schema_signature(new_defs[name])
    )

    lines = [f"### API changes {old_label} → {new_label}", ""]
    if not any((added, removed, changed, defs_added, defs_removed, defs_changed)):
        lines.append("_No structural changes._")
        return "\n".join(lines) + "\n"

    def section(title: str, entries: list, render) -> None:
        if entries:
            lines.append(f"**{title}** ({len(entries)})")
            lines.extend(f"- {render(e)}" for e in entries[:40])
            if len(entries) > 40:
                lines.append(f"- … and {len(entries) - 40} more")
            lines.append("")

    render_op = lambda key: f"`{key[0].upper()} {key[1]}`"  # noqa: E731
    section("Added operations", added, render_op)
    section("Removed operations", removed, render_op)
    section("Changed operations", changed, render_op)
    section("Added definitions", defs_added, lambda n: f"`{n}`")
    section("Removed definitions", defs_removed, lambda n: f"`{n}`")
    section("Changed definitions", defs_changed, lambda n: f"`{n}`")
    return "\n".join(lines).rstrip() + "\n"
