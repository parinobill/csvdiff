"""Baseline management: save and load a CSV diff result as a baseline for future comparisons."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from csvdiff.differ import DiffResult, RowChange


def _change_to_dict(change: RowChange) -> dict:
    return {
        "key": change.key,
        "change_type": change.change_type,
        "old_row": change.old_row,
        "new_row": change.new_row,
    }


def _change_from_dict(d: dict) -> RowChange:
    return RowChange(
        key=d["key"],
        change_type=d["change_type"],
        old_row=d.get("old_row"),
        new_row=d.get("new_row"),
    )


def save_baseline(result: DiffResult, path: str | os.PathLike) -> None:
    """Persist a DiffResult to a JSON baseline file."""
    data = {
        "key_column": result.key_column,
        "changes": [_change_to_dict(c) for c in result.changes],
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_baseline(path: str | os.PathLike) -> DiffResult:
    """Load a DiffResult from a JSON baseline file."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    changes = [_change_from_dict(c) for c in raw.get("changes", [])]
    return DiffResult(key_column=raw["key_column"], changes=changes)


def diff_against_baseline(
    current: DiffResult, baseline: DiffResult
) -> tuple[list[RowChange], list[RowChange]]:
    """Return (new_changes, resolved_changes) relative to the baseline.

    new_changes     – appear in current but not in baseline.
    resolved_changes – appeared in baseline but are gone in current.
    """
    def _key(c: RowChange) -> tuple:
        return (c.key, c.change_type)

    baseline_keys = {_key(c) for c in baseline.changes}
    current_keys = {_key(c) for c in current.changes}

    new_changes = [c for c in current.changes if _key(c) not in baseline_keys]
    resolved_changes = [c for c in baseline.changes if _key(c) not in current_keys]
    return new_changes, resolved_changes


def baseline_summary(new: list[RowChange], resolved: list[RowChange]) -> str:
    """Return a human-readable summary of changes relative to a baseline."""
    lines = []
    if not new and not resolved:
        lines.append("No changes relative to baseline.")
    else:
        if new:
            lines.append(f"New changes since baseline: {len(new)}")
        if resolved:
            lines.append(f"Resolved since baseline:    {len(resolved)}")
    return "\n".join(lines)
