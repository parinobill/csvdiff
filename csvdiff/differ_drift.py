"""Detect schema drift between two CSV files (added/removed/reordered columns)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class SchemaDrift:
    added_columns: List[str] = field(default_factory=list)
    removed_columns: List[str] = field(default_factory=list)
    reordered: bool = False
    old_order: List[str] = field(default_factory=list)
    new_order: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.added_columns or self.removed_columns or self.reordered)

    def summary(self) -> str:
        if not self.has_drift:
            return "No schema drift detected."
        parts: List[str] = []
        if self.added_columns:
            cols = ", ".join(self.added_columns)
            parts.append(f"Added columns: {cols}")
        if self.removed_columns:
            cols = ", ".join(self.removed_columns)
            parts.append(f"Removed columns: {cols}")
        if self.reordered:
            parts.append("Column order changed.")
        return " | ".join(parts)

    def as_dict(self) -> dict:
        return {
            "added_columns": self.added_columns,
            "removed_columns": self.removed_columns,
            "reordered": self.reordered,
            "old_order": self.old_order,
            "new_order": self.new_order,
        }


def detect_drift(
    old_columns: Sequence[str],
    new_columns: Sequence[str],
) -> SchemaDrift:
    """Compare two ordered column lists and return a SchemaDrift report."""
    old_set = set(old_columns)
    new_set = set(new_columns)

    added = [c for c in new_columns if c not in old_set]
    removed = [c for c in old_columns if c not in new_set]

    common_old = [c for c in old_columns if c in new_set]
    common_new = [c for c in new_columns if c in old_set]
    reordered = common_old != common_new

    return SchemaDrift(
        added_columns=added,
        removed_columns=removed,
        reordered=reordered,
        old_order=list(old_columns),
        new_order=list(new_columns),
    )
