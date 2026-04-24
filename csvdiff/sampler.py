"""Random and deterministic sampling of DiffResult changes."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class SampleOptions:
    n: Optional[int] = None          # absolute number of changes to keep
    fraction: Optional[float] = None  # fraction in (0, 1]
    seed: Optional[int] = None        # for reproducible sampling
    change_types: Optional[List[str]] = None  # limit to these types


def _filter_by_types(
    changes: List[RowChange], types: Optional[List[str]]
) -> List[RowChange]:
    if not types:
        return changes
    allowed = {t.lower() for t in types}
    return [c for c in changes if c.change_type.lower() in allowed]


def sample_diff(result: DiffResult, opts: SampleOptions) -> DiffResult:
    """Return a new DiffResult containing a sampled subset of changes."""
    if opts.n is None and opts.fraction is None:
        raise ValueError("Either 'n' or 'fraction' must be specified.")
    if opts.n is not None and opts.fraction is not None:
        raise ValueError("Specify only one of 'n' or 'fraction', not both.")
    if opts.fraction is not None and not (0 < opts.fraction <= 1.0):
        raise ValueError("'fraction' must be in the range (0, 1].")

    rng = random.Random(opts.seed)

    pool = _filter_by_types(result.changes, opts.change_types)

    if opts.fraction is not None:
        k = max(1, int(len(pool) * opts.fraction))
    else:
        k = min(opts.n, len(pool))  # type: ignore[arg-type]

    sampled = rng.sample(pool, k) if k < len(pool) else list(pool)

    return DiffResult(changes=sampled, unchanged=result.unchanged)


def sample_summary(original: DiffResult, sampled: DiffResult) -> str:
    """Human-readable description of the sampling operation."""
    orig_n = len(original.changes)
    samp_n = len(sampled.changes)
    if orig_n == 0:
        return "No changes to sample."
    pct = 100.0 * samp_n / orig_n
    return (
        f"Sampled {samp_n} of {orig_n} change(s) ({pct:.1f}%); "
        f"{len(sampled.unchanged)} row(s) unchanged."
    )
