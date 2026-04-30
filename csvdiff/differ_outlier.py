"""Detect statistical outliers among numeric field changes."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class OutlierChange:
    change: RowChange
    field_name: str
    old_value: float
    new_value: float
    delta: float
    z_score: float

    def __str__(self) -> str:  # noqa: D105
        return (
            f"[OUTLIER] key={self.change.key} field={self.field_name} "
            f"{self.old_value} -> {self.new_value} "
            f"(delta={self.delta:+.4g}, z={self.z_score:.2f})"
        )


@dataclass
class OutlierResult:
    outliers: List[OutlierChange] = field(default_factory=list)
    field_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def summary(self) -> str:
        if not self.outliers:
            return "No numeric outliers detected."
        lines = [f"{len(self.outliers)} outlier(s) detected:"]
        for o in self.outliers:
            lines.append(f"  {o}")
        return "\n".join(lines)


def _try_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _compute_stats(values: List[float]) -> Dict[str, float]:
    n = len(values)
    if n == 0:
        return {"mean": 0.0, "std": 0.0, "n": 0.0}
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n if n > 1 else 0.0
    return {"mean": mean, "std": math.sqrt(variance), "n": float(n)}


def detect_outliers(result: DiffResult, z_threshold: float = 2.0) -> OutlierResult:
    """Return changes whose numeric field deltas are statistical outliers."""
    field_deltas: Dict[str, List[tuple]] = {}

    for change in result.changes:
        if change.change_type != "modified":
            continue
        for fname, (old, new) in (change.fields_changed or {}).items():
            old_f = _try_float(old)
            new_f = _try_float(new)
            if old_f is None or new_f is None:
                continue
            field_deltas.setdefault(fname, []).append((change, old_f, new_f, new_f - old_f))

    out = OutlierResult()
    for fname, entries in field_deltas.items():
        deltas = [e[3] for e in entries]
        stats = _compute_stats(deltas)
        out.field_stats[fname] = stats
        std = stats["std"]
        mean = stats["mean"]
        for change, old_f, new_f, delta in entries:
            z = (delta - mean) / std if std > 0 else 0.0
            if abs(z) >= z_threshold:
                out.outliers.append(
                    OutlierChange(
                        change=change,
                        field_name=fname,
                        old_value=old_f,
                        new_value=new_f,
                        delta=delta,
                        z_score=z,
                    )
                )
    return out
