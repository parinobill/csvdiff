"""Limit the number of changes returned in a DiffResult."""

from dataclasses import dataclass
from typing import Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class LimitOptions:
    max_changes: Optional[int] = None
    max_added: Optional[int] = None
    max_removed: Optional[int] = None
    max_modified: Optional[int] = None


def _cap(changes: list, limit: Optional[int]) -> list:
    """Return at most *limit* items from *changes*, or all if limit is None."""
    if limit is None:
        return changes
    return changes[:limit]


def limit_diff(result: DiffResult, opts: LimitOptions) -> DiffResult:
    """Return a new DiffResult with changes capped according to *opts*.

    When *max_changes* is set it acts as a global ceiling applied after the
    per-type caps.
    """
    added = _cap(
        [c for c in result.changes if c.change_type == "added"],
        opts.max_added,
    )
    removed = _cap(
        [c for c in result.changes if c.change_type == "removed"],
        opts.max_removed,
    )
    modified = _cap(
        [c for c in result.changes if c.change_type == "modified"],
        opts.max_modified,
    )

    combined: list[RowChange] = added + removed + modified

    if opts.max_changes is not None:
        combined = combined[: opts.max_changes]

    return DiffResult(
        changes=combined,
        unchanged_count=result.unchanged_count,
    )


def limit_summary(result: DiffResult, opts: LimitOptions) -> str:
    """Return a one-line summary describing how many changes were kept."""
    limited = limit_diff(result, opts)
    total_before = len(result.changes)
    total_after = len(limited.changes)
    if total_after == total_before:
        return f"All {total_before} change(s) kept (no limit applied)."
    return (
        f"{total_after} of {total_before} change(s) kept after applying limits."
    )
