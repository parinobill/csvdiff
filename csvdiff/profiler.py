"""Profile a DiffResult to produce column-level change statistics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from csvdiff.differ import DiffResult, RowChange


@dataclass
class ColumnProfile:
    """Change statistics for a single column."""

    column: str
    change_count: int = 0
    affected_keys: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"{self.column}: {self.change_count} change(s) "
            f"across {len(self.affected_keys)} row(s)"
        )


@dataclass
class DiffProfile:
    """Aggregated per-column profile of a DiffResult."""

    total_rows_affected: int
    added: int
    removed: int
    modified: int
    column_profiles: Dict[str, ColumnProfile] = field(default_factory=dict)

    def most_changed_columns(self, top_n: int = 5) -> List[ColumnProfile]:
        """Return up to *top_n* columns sorted by change count descending."""
        sorted_cols = sorted(
            self.column_profiles.values(),
            key=lambda cp: cp.change_count,
            reverse=True,
        )
        return sorted_cols[:top_n]


def profile_diff(result: DiffResult) -> DiffProfile:
    """Compute a DiffProfile from a DiffResult."""
    added = 0
    removed = 0
    modified = 0
    col_counts: Dict[str, int] = defaultdict(int)
    col_keys: Dict[str, List[str]] = defaultdict(list)

    for change in result.changes:
        key_str = str(change.key)
        if change.old is None:
            added += 1
        elif change.new is None:
            removed += 1
        else:
            modified += 1
            old, new = change.old, change.new
            for col in set(list(old.keys()) + list(new.keys())):
                if old.get(col) != new.get(col):
                    col_counts[col] += 1
                    col_keys[col].append(key_str)

    column_profiles = {
        col: ColumnProfile(
            column=col,
            change_count=col_counts[col],
            affected_keys=col_keys[col],
        )
        for col in col_counts
    }

    return DiffProfile(
        total_rows_affected=len(result.changes),
        added=added,
        removed=removed,
        modified=modified,
        column_profiles=column_profiles,
    )
