"""Utilities for sorting CSV diff results."""

from typing import List, Optional
from csvdiff.differ import DiffResult, RowChange


SORTABLE_FIELDS = ("key", "change_type")


def sort_changes(
    result: DiffResult,
    by: str = "key",
    reverse: bool = False,
) -> DiffResult:
    """Return a new DiffResult with changes sorted by the given field.

    Args:
        result: The DiffResult to sort.
        by: Field to sort by — 'key' or 'change_type'.
        reverse: If True, sort in descending order.

    Returns:
        A new DiffResult instance with sorted changes.

    Raises:
        ValueError: If `by` is not a recognised sort field.
    """
    if by not in SORTABLE_FIELDS:
        raise ValueError(
            f"Cannot sort by {by!r}. Choose one of: {', '.join(SORTABLE_FIELDS)}"
        )

    def _key(change: RowChange):
        if by == "key":
            return str(change.key)
        if by == "change_type":
            return change.change_type
        return ""

    sorted_changes: List[RowChange] = sorted(result.changes, key=_key, reverse=reverse)

    return DiffResult(
        added=_filter_by_type(sorted_changes, "added"),
        removed=_filter_by_type(sorted_changes, "removed"),
        changed=_filter_by_type(sorted_changes, "changed"),
    )


def _filter_by_type(changes: List[RowChange], change_type: str) -> List[RowChange]:
    return [c for c in changes if c.change_type == change_type]


def get_sort_key_values(result: DiffResult) -> List[str]:
    """Return a list of all key values present in the diff, in order."""
    return [str(c.key) for c in result.changes]
