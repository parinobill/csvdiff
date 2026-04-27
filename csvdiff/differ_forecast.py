"""Forecast future change trends based on ledger history."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from csvdiff.differ_ledger import LedgerEntry


@dataclass
class ForecastPoint:
    """A single forecasted data point."""
    run_index: int
    predicted_added: float
    predicted_removed: float
    predicted_modified: float

    @property
    def predicted_total(self) -> float:
        return self.predicted_added + self.predicted_removed + self.predicted_modified

    def __str__(self) -> str:
        return (
            f"Run {self.run_index}: +{self.predicted_added:.1f} "
            f"-{self.predicted_removed:.1f} ~{self.predicted_modified:.1f}"
        )


@dataclass
class ForecastResult:
    points: List[ForecastPoint] = field(default_factory=list)
    trend_added: float = 0.0
    trend_removed: float = 0.0
    trend_modified: float = 0.0

    def summary(self) -> str:
        lines = [f"Forecast ({len(self.points)} step(s)):"]
        for p in self.points:
            lines.append(f"  {p}")
        lines.append(
            f"Trend per run: +{self.trend_added:.2f} "
            f"-{self.trend_removed:.2f} ~{self.trend_modified:.2f}"
        )
        return "\n".join(lines)


def _linear_trend(values: List[float]) -> float:
    """Return the average delta between consecutive values."""
    if len(values) < 2:
        return 0.0
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    return sum(deltas) / len(deltas)


def forecast_from_ledger(
    entries: List[LedgerEntry],
    steps: int = 3,
) -> ForecastResult:
    """Produce a naive linear forecast from ledger history."""
    if not entries:
        return ForecastResult()

    added_vals = [float(e.added) for e in entries]
    removed_vals = [float(e.removed) for e in entries]
    modified_vals = [float(e.modified) for e in entries]

    trend_a = _linear_trend(added_vals)
    trend_r = _linear_trend(removed_vals)
    trend_m = _linear_trend(modified_vals)

    last_a = added_vals[-1]
    last_r = removed_vals[-1]
    last_m = modified_vals[-1]

    points: List[ForecastPoint] = []
    for i in range(1, steps + 1):
        points.append(ForecastPoint(
            run_index=len(entries) + i,
            predicted_added=max(0.0, last_a + trend_a * i),
            predicted_removed=max(0.0, last_r + trend_r * i),
            predicted_modified=max(0.0, last_m + trend_m * i),
        ))

    return ForecastResult(
        points=points,
        trend_added=trend_a,
        trend_removed=trend_r,
        trend_modified=trend_m,
    )
