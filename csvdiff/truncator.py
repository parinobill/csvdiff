"""Truncate long field values in diff output for readability."""

from typing import Optional
from csvdiff.differ import DiffResult, RowChange

DEFAULT_MAX_LEN = 60
ELLIPSIS = "..."


def truncate_value(value: str, max_len: int = DEFAULT_MAX_LEN) -> str:
    """Truncate a single string value if it exceeds max_len."""
    if len(value) <= max_len:
        return value
    keep = max_len - len(ELLIPSIS)
    return value[:keep] + ELLIPSIS


def truncate_change(change: RowChange, max_len: int = DEFAULT_MAX_LEN) -> RowChange:
    """Return a new RowChange with all field values truncated."""
    truncated_before = (
        {k: truncate_value(str(v), max_len) for k, v in change.before.items()}
        if change.before
        else None
    )
    truncated_after = (
        {k: truncate_value(str(v), max_len) for k, v in change.after.items()}
        if change.after
        else None
    )
    return RowChange(
        change_type=change.change_type,
        key=change.key,
        before=truncated_before,
        after=truncated_after,
    )


def truncate_diff(result: DiffResult, max_len: int = DEFAULT_MAX_LEN) -> DiffResult:
    """Return a new DiffResult with all change field values truncated."""
    truncated_changes = [truncate_change(c, max_len) for c in result.changes]
    return DiffResult(changes=truncated_changes)
