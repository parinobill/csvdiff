"""Rank changes by a numeric field value to surface the most impactful diffs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class RankedChange:
    change: RowChange
    rank: int
    score: float

    def __str__(self) -> str:
        return f"[#{self.rank} score={self.score:.4f}] {self.change}"


@dataclass
class RankResult:
    ranked: List[RankedChange] = field(default_factory=list)
    rank_field: str = ""
    top_n: Optional[int] = None

    def top(self) -> List[RankedChange]:
        cap = self.top_n if self.top_n is not None else len(self.ranked)
        return self.ranked[:cap]

    def summary(self) -> str:
        shown = self.top()
        if not shown:
            return "No changes to rank."
        lines = [f"Top {len(shown)} change(s) ranked by '{self.rank_field}':"]
        for rc in shown:
            lines.append(f"  {rc}")
        return "\n".join(lines)


def _extract_score(change: RowChange, rank_field: str) -> float:
    """Return the absolute numeric delta for *rank_field*, or 0.0 if unavailable."""
    if rank_field in (change.after or {}):
        after_val = (change.after or {}).get(rank_field, "")
        before_val = (change.before or {}).get(rank_field, "")
        try:
            return abs(float(after_val) - float(before_val))
        except (TypeError, ValueError):
            pass
    for src in (change.after, change.before):
        if src and rank_field in src:
            try:
                return abs(float(src[rank_field]))
            except (TypeError, ValueError):
                pass
    return 0.0


def rank_diff(
    result: DiffResult,
    rank_field: str,
    top_n: Optional[int] = None,
    ascending: bool = False,
) -> RankResult:
    """Rank all changes in *result* by the numeric delta of *rank_field*."""
    if not rank_field:
        raise ValueError("rank_field must be a non-empty string")

    scored = [
        (change, _extract_score(change, rank_field))
        for change in result.changes
    ]
    scored.sort(key=lambda t: t[1], reverse=not ascending)

    ranked = [
        RankedChange(change=ch, rank=idx + 1, score=sc)
        for idx, (ch, sc) in enumerate(scored)
    ]

    return RankResult(ranked=ranked, rank_field=rank_field, top_n=top_n)
