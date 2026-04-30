"""Watch-report module: accumulates diff results across watcher cycles
and produces a rolling summary with trend indicators."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csvdiff.stats import DiffStats, compute_stats
from csvdiff.differ import DiffResult


@dataclass
class WatchReportEntry:
    cycle: int
    stats: DiffStats
    label: str = ""

    def trend_vs(self, previous: Optional["WatchReportEntry"]) -> str:
        if previous is None:
            return "~"
        delta = self.stats.changed - previous.stats.changed
        if delta > 0:
            return f"+{delta}"
        if delta < 0:
            return str(delta)
        return "="

    def __str__(self) -> str:
        return (
            f"[cycle {self.cycle}] "
            f"added={self.stats.added} "
            f"removed={self.stats.removed} "
            f"modified={self.stats.modified}"
        )


@dataclass
class WatchReport:
    entries: List[WatchReportEntry] = field(default_factory=list)

    def record(self, result: DiffResult, label: str = "") -> WatchReportEntry:
        cycle = len(self.entries) + 1
        entry = WatchReportEntry(cycle=cycle, stats=compute_stats(result), label=label)
        self.entries.append(entry)
        return entry

    def latest(self) -> Optional[WatchReportEntry]:
        return self.entries[-1] if self.entries else None

    def summary(self) -> str:
        if not self.entries:
            return "No cycles recorded."
        lines = ["Watch report summary:", f"  Cycles recorded: {len(self.entries)}"]
        for i, entry in enumerate(self.entries):
            prev = self.entries[i - 1] if i > 0 else None
            trend = entry.trend_vs(prev)
            lines.append(f"  {entry}  trend={trend}")
        total_changes = sum(e.stats.changed for e in self.entries)
        lines.append(f"  Total changes across all cycles: {total_changes}")
        return "\n".join(lines)


def build_watch_report() -> WatchReport:
    """Factory returning a fresh WatchReport."""
    return WatchReport()
