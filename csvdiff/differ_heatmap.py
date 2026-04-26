"""Heatmap: count how many times each (row_key, field) cell changed."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from csvdiff.differ import DiffResult, RowChange


@dataclass
class HeatmapCell:
    row_key: str
    field_name: str
    change_count: int = 0

    def __str__(self) -> str:
        return f"{self.row_key}:{self.field_name} ({self.change_count})"


@dataclass
class DiffHeatmap:
    """Sparse matrix of (row_key, field) -> change count."""
    _data: Dict[Tuple[str, str], int] = field(default_factory=dict)

    def increment(self, row_key: str, field_name: str, amount: int = 1) -> None:
        key = (row_key, field_name)
        self._data[key] = self._data.get(key, 0) + amount

    def get(self, row_key: str, field_name: str) -> int:
        return self._data.get((row_key, field_name), 0)

    def all_cells(self) -> List[HeatmapCell]:
        return [
            HeatmapCell(row_key=k[0], field_name=k[1], change_count=v)
            for k, v in sorted(self._data.items())
        ]

    def top_cells(self, n: int) -> List[HeatmapCell]:
        cells = self.all_cells()
        return sorted(cells, key=lambda c: c.change_count, reverse=True)[:n]

    def hottest_field(self) -> Optional[str]:
        if not self._data:
            return None
        field_totals: Dict[str, int] = defaultdict(int)
        for (_, f), count in self._data.items():
            field_totals[f] += count
        return max(field_totals, key=lambda f: field_totals[f])

    def summary(self) -> str:
        total = sum(self._data.values())
        unique_cells = len(self._data)
        return f"{total} total changes across {unique_cells} distinct (row, field) cells"


def build_heatmap(result: DiffResult) -> DiffHeatmap:
    """Build a heatmap from a DiffResult."""
    hm = DiffHeatmap()
    for change in result.changes:
        row_key = change.key
        if change.change_type == "modified":
            for f, (old, new) in change.field_changes.items():
                if old != new:
                    hm.increment(row_key, f)
        elif change.change_type == "added":
            for f in (change.new_row or {}):
                hm.increment(row_key, f)
        elif change.change_type == "removed":
            for f in (change.old_row or {}):
                hm.increment(row_key, f)
    return hm
