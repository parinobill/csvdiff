"""Rebase a patch against a newer baseline to resolve conflicts."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from csvdiff.differ import DiffResult, RowChange


@dataclass
class RebaseConflict:
    key: str
    reason: str
    ours: Optional[RowChange]
    theirs: Optional[RowChange]

    def __str__(self) -> str:
        return f"Conflict on key={self.key!r}: {self.reason}"


@dataclass
class RebaseResult:
    rebased: DiffResult
    conflicts: List[RebaseConflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def summary(self) -> str:
        n = len(self.rebased.changes)
        c = len(self.conflicts)
        return f"Rebased {n} change(s), {c} conflict(s)"


def _index_by_key(result: DiffResult) -> dict:
    return {ch.key: ch for ch in result.changes}


def rebase_patch(original: DiffResult, upstream: DiffResult) -> RebaseResult:
    """Rebase *original* patch on top of *upstream* changes.

    Changes that do not conflict are kept as-is.  Where both patches
    touch the same key the upstream wins and a RebaseConflict is recorded.
    """
    orig_index = _index_by_key(original)
    up_index = _index_by_key(upstream)

    conflicts: List[RebaseConflict] = []
    kept: List[RowChange] = []

    for key, change in orig_index.items():
        if key in up_index:
            conflicts.append(
                RebaseConflict(
                    key=key,
                    reason="both patches modify the same row",
                    ours=change,
                    theirs=up_index[key],
                )
            )
        else:
            kept.append(change)

    # Include upstream changes that are not in original
    for key, change in up_index.items():
        if key not in orig_index:
            kept.append(change)

    rebased = DiffResult(changes=kept)
    return RebaseResult(rebased=rebased, conflicts=conflicts)


def rebase_summary(result: RebaseResult) -> str:
    lines = [result.summary()]
    for c in result.conflicts:
        lines.append(f"  ! {c}")
    return "\n".join(lines)
