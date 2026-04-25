"""Pivot a DiffResult: reorganise changes by field name rather than by row key."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class FieldPivot:
    """All changes that touched a particular field."""

    field_name: str
    added_values: List[str] = field(default_factory=list)
    removed_values: List[str] = field(default_factory=list)
    old_values: List[str] = field(default_factory=list)
    new_values: List[str] = field(default_factory=list)

    @property
    def total_touches(self) -> int:
        return (
            len(self.added_values)
            + len(self.removed_values)
            + len(self.old_values)
        )

    def summary(self) -> str:
        parts = []
        if self.added_values:
            parts.append(f"+{len(self.added_values)} added")
        if self.removed_values:
            parts.append(f"-{len(self.removed_values)} removed")
        if self.old_values:
            parts.append(f"~{len(self.old_values)} modified")
        touch_str = ", ".join(parts) if parts else "no changes"
        return f"{self.field_name}: {touch_str}"


def pivot_diff(result: DiffResult) -> Dict[str, FieldPivot]:
    """Return a mapping of field_name -> FieldPivot from a DiffResult."""
    pivots: Dict[str, FieldPivot] = {}

    def _get(name: str) -> FieldPivot:
        if name not in pivots:
            pivots[name] = FieldPivot(field_name=name)
        return pivots[name]

    for change in result.added:
        for col, val in change.new_row.items():
            _get(col).added_values.append(val)

    for change in result.removed:
        for col, val in change.old_row.items():
            _get(col).removed_values.append(val)

    for change in result.modified:
        for col in change.changed_fields:
            p = _get(col)
            p.old_values.append(change.old_row.get(col, ""))
            p.new_values.append(change.new_row.get(col, ""))

    return pivots


def top_changed_fields(
    result: DiffResult, n: Optional[int] = None
) -> List[FieldPivot]:
    """Return FieldPivots sorted by total_touches descending, optionally capped at n."""
    pivots = pivot_diff(result)
    ranked = sorted(pivots.values(), key=lambda p: p.total_touches, reverse=True)
    return ranked[:n] if n is not None else ranked
