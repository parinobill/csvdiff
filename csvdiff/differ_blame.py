"""Blame module: annotate each change with the first diff result that introduced it."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class BlamedChange:
    """A change paired with the label of the diff that introduced it."""

    change: RowChange
    source_label: str

    def __str__(self) -> str:
        return f"[{self.source_label}] {self.change}"


@dataclass
class BlameResult:
    """Collection of blamed changes."""

    blamed: List[BlamedChange] = field(default_factory=list)

    def by_label(self, label: str) -> List[BlamedChange]:
        return [b for b in self.blamed if b.source_label == label]

    def labels(self) -> List[str]:
        seen: List[str] = []
        for b in self.blamed:
            if b.source_label not in seen:
                seen.append(b.source_label)
        return seen

    def summary(self) -> str:
        if not self.blamed:
            return "No changes to blame."
        lines = []
        for label in self.labels():
            count = len(self.by_label(label))
            lines.append(f"  {label}: {count} change(s)")
        return "Blame summary:\n" + "\n".join(lines)


def _change_key(change: RowChange) -> tuple:
    """Return a hashable key identifying a change uniquely."""
    return (change.change_type, change.key_value)


def blame_changes(
    labeled_results: List[tuple],  # list of (label: str, DiffResult)
) -> BlameResult:
    """Assign each unique change to the earliest diff result that contains it.

    Args:
        labeled_results: ordered list of (label, DiffResult) pairs, earliest first.

    Returns:
        BlameResult with each change attributed to its first-seen source.
    """
    seen: Dict[tuple, str] = {}
    blamed: List[BlamedChange] = []

    for label, result in labeled_results:
        for change in result.changes:
            key = _change_key(change)
            if key not in seen:
                seen[key] = label
                blamed.append(BlamedChange(change=change, source_label=label))

    return BlameResult(blamed=blamed)
