"""Compute summary statistics from a DiffResult."""
from dataclasses import dataclass
from typing import Dict
from csvdiff.differ import DiffResult


@dataclass
class DiffStats:
    added: int
    removed: int
    modified: int
    unchanged: int
    total_rows: int

    @property
    def changed(self) -> int:
        return self.added + self.removed + self.modified

    def as_dict(self) -> Dict[str, int]:
        return {
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "unchanged": self.unchanged,
            "total_rows": self.total_rows,
            "changed": self.changed,
        }

    def __str__(self) -> str:
        return (
            f"Added: {self.added}, Removed: {self.removed}, "
            f"Modified: {self.modified}, Unchanged: {self.unchanged}"
        )


def compute_stats(result: DiffResult, total_rows: int = 0) -> DiffStats:
    """Compute counts of each change type from a DiffResult."""
    added = sum(1 for c in result.changes if c.change_type == "added")
    removed = sum(1 for c in result.changes if c.change_type == "removed")
    modified = sum(1 for c in result.changes if c.change_type == "modified")
    unchanged = max(0, total_rows - added - removed - modified)
    return DiffStats(
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
        total_rows=total_rows,
    )
