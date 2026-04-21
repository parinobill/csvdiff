"""Deduplication utilities for CSV diff results.

Provides functions to detect and remove duplicate RowChange entries
from a DiffResult, with configurable strategies.
"""

from typing import List, Literal, Optional
from csvdiff.differ import DiffResult, RowChange

DedupeStrategy = Literal["first", "last"]


def _change_key(change: RowChange) -> tuple:
    """Return a hashable key identifying a change by its key value and type."""
    return (change.key_value, change.change_type)


def find_duplicates(result: DiffResult) -> List[RowChange]:
    """Return a list of RowChange entries that are duplicates (all but first occurrence)."""
    seen = set()
    duplicates = []
    for change in result.changes:
        k = _change_key(change)
        if k in seen:
            duplicates.append(change)
        else:
            seen.add(k)
    return duplicates


def deduplicate(
    result: DiffResult,
    strategy: DedupeStrategy = "first",
) -> DiffResult:
    """Return a new DiffResult with duplicate changes removed.

    Args:
        result: The original DiffResult.
        strategy: 'first' keeps the first occurrence; 'last' keeps the last.

    Returns:
        A new DiffResult with unique changes only.
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown deduplication strategy: {strategy!r}")

    changes = result.changes if strategy == "first" else list(reversed(result.changes))
    seen = set()
    unique = []
    for change in changes:
        k = _change_key(change)
        if k not in seen:
            seen.add(k)
            unique.append(change)

    if strategy == "last":
        unique = list(reversed(unique))

    return DiffResult(changes=unique, unchanged_count=result.unchanged_count)


def deduplicate_summary(original: DiffResult, deduped: DiffResult) -> str:
    """Return a human-readable summary of what was removed."""
    removed = len(original.changes) - len(deduped.changes)
    if removed == 0:
        return "No duplicate changes found."
    return (
        f"Removed {removed} duplicate change(s); "
        f"{len(deduped.changes)} unique change(s) remain."
    )
