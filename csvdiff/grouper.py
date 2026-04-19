"""Group diff changes by a field value or change type."""

from collections import defaultdict
from typing import Dict, List, Optional
from csvdiff.differ import DiffResult, RowChange


def group_by_change_type(result: DiffResult) -> Dict[str, List[RowChange]]:
    """Return changes bucketed by their change type (added/removed/modified)."""
    groups: Dict[str, List[RowChange]] = defaultdict(list)
    for change in result.changes:
        groups[change.change_type].append(change)
    return dict(groups)


def group_by_field_value(result: DiffResult, field: str) -> Dict[str, List[RowChange]]:
    """Return changes bucketed by the value of *field* in the row snapshot.

    For added/modified rows the after-snapshot is used; for removed rows the
    before-snapshot is used.  Rows where the field is absent are placed under
    the empty-string key.
    """
    groups: Dict[str, List[RowChange]] = defaultdict(list)
    for change in result.changes:
        row = change.after if change.after is not None else change.before
        value = (row or {}).get(field, "")
        groups[str(value)].append(change)
    return dict(groups)


def group_summary(groups: Dict[str, List[RowChange]]) -> Dict[str, int]:
    """Return a dict mapping each group key to its change count."""
    return {k: len(v) for k, v in groups.items()}
