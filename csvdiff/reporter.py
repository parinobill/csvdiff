"""Generates structured report output (JSON/text) from a DiffResult."""
from __future__ import annotations
import json
from typing import Literal
from csvdiff.differ import DiffResult

OutputFormat = Literal["text", "json"]


def _diff_to_dict(result: DiffResult) -> dict:
    return {
        "added": [
            {"key": change.key, "row": change.new_row}
            for change in result.added
        ],
        "removed": [
            {"key": change.key, "row": change.old_row}
            for change in result.removed
        ],
        "changed": [
            {
                "key": change.key,
                "fields": {
                    field: {"old": old, "new": new}
                    for field, old, new in change.field_changes
                },
            }
            for change in result.changed
        ],
        "summary": {
            "added": len(result.added),
            "removed": len(result.removed),
            "changed": len(result.changed),
        },
    }


def render_report(result: DiffResult, fmt: OutputFormat = "text") -> str:
    """Return a report string in the requested format."""
    if fmt == "json":
        return json.dumps(_diff_to_dict(result), indent=2)

    if not result.has_changes():
        return "No differences found."

    lines: list[str] = []
    for change in result.added:
        lines.append(f"+ [{change.key}] row added: {change.new_row}")
    for change in result.removed:
        lines.append(f"- [{change.key}] row removed: {change.old_row}")
    for change in result.changed:
        for field, old, new in change.field_changes:
            lines.append(f"~ [{change.key}] {field}: {old!r} -> {new!r}")
    lines.append(result.summary())
    return "\n".join(lines)
