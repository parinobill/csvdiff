"""Threshold filtering: suppress changes below a significance threshold."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csvdiff.differ import DiffResult, RowChange
from csvdiff.stats import compute_stats


@dataclass
class ThresholdOptions:
    """Options controlling which changes survive threshold filtering."""
    min_changed_fields: int = 1          # drop modified rows with fewer changed fields
    max_pct_added: Optional[float] = None    # drop result if added% exceeds this
    max_pct_removed: Optional[float] = None  # drop result if removed% exceeds this
    require_min_rows: int = 0            # ignore diff if total rows below this count


@dataclass
class ThresholdResult:
    kept: List[RowChange] = field(default_factory=list)
    dropped: List[RowChange] = field(default_factory=list)
    suppressed: bool = False  # True when the whole diff was suppressed

    def summary(self) -> str:
        if self.suppressed:
            return "Diff suppressed: did not meet threshold requirements."
        return (
            f"Threshold filter: {len(self.kept)} change(s) kept, "
            f"{len(self.dropped)} dropped."
        )


def _changed_field_count(change: RowChange) -> int:
    """Return number of fields that actually changed in a modified row."""
    if change.change_type != "modified":
        return 0
    old = change.old_row or {}
    new = change.new_row or {}
    return sum(1 for k in new if old.get(k) != new.get(k))


def apply_threshold(result: DiffResult, opts: ThresholdOptions) -> ThresholdResult:
    """Filter *result* according to *opts*; return a ThresholdResult."""
    stats = compute_stats(result)
    total = stats.total

    if total < opts.require_min_rows:
        return ThresholdResult(suppressed=True)

    if opts.max_pct_added is not None and total > 0:
        pct = stats.added / total * 100
        if pct > opts.max_pct_added:
            return ThresholdResult(suppressed=True)

    if opts.max_pct_removed is not None and total > 0:
        pct = stats.removed / total * 100
        if pct > opts.max_pct_removed:
            return ThresholdResult(suppressed=True)

    kept: List[RowChange] = []
    dropped: List[RowChange] = []

    for change in result.changes:
        if change.change_type == "modified":
            if _changed_field_count(change) < opts.min_changed_fields:
                dropped.append(change)
                continue
        kept.append(change)

    return ThresholdResult(kept=kept, dropped=dropped)
