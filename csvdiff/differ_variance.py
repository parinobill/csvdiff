"""Variance analysis: detect fields whose values change most across a diff."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


def _try_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass
class FieldVariance:
    field_name: str
    change_count: int = 0
    numeric_deltas: List[float] = field(default_factory=list)

    @property
    def mean_delta(self) -> Optional[float]:
        if not self.numeric_deltas:
            return None
        return sum(self.numeric_deltas) / len(self.numeric_deltas)

    @property
    def max_delta(self) -> Optional[float]:
        return max(self.numeric_deltas, default=None)

    def summary(self) -> str:
        parts = [f"{self.field_name}: {self.change_count} change(s)"]
        if self.mean_delta is not None:
            parts.append(f"mean_delta={self.mean_delta:.4g}")
        if self.max_delta is not None:
            parts.append(f"max_delta={self.max_delta:.4g}")
        return ", ".join(parts)


@dataclass
class VarianceResult:
    fields: Dict[str, FieldVariance] = field(default_factory=dict)

    def top(self, n: int = 5) -> List[FieldVariance]:
        sorted_fields = sorted(
            self.fields.values(), key=lambda fv: fv.change_count, reverse=True
        )
        return sorted_fields[:n]

    def summary(self) -> str:
        if not self.fields:
            return "No field variance detected."
        lines = ["Field variance summary:"]
        for fv in self.top():
            lines.append(f"  {fv.summary()}")
        return "\n".join(lines)


def compute_variance(result: DiffResult) -> VarianceResult:
    """Analyse which fields vary most across modified rows."""
    variance = VarianceResult()

    for change in result.changes:
        if change.change_type != "modified":
            continue
        old = change.old_row or {}
        new = change.new_row or {}
        all_fields = set(old) | set(new)
        for fname in all_fields:
            old_val = old.get(fname, "")
            new_val = new.get(fname, "")
            if old_val == new_val:
                continue
            if fname not in variance.fields:
                variance.fields[fname] = FieldVariance(field_name=fname)
            fv = variance.fields[fname]
            fv.change_count += 1
            old_f = _try_float(old_val)
            new_f = _try_float(new_val)
            if old_f is not None and new_f is not None:
                fv.numeric_deltas.append(abs(new_f - old_f))

    return variance
