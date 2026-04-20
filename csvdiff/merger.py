"""Merge two DiffResults into a single consolidated DiffResult."""

from typing import Dict, List, Optional
from csvdiff.differ import DiffResult, RowChange


def _index_changes(result: DiffResult) -> Dict[str, RowChange]:
    """Build a dict mapping row key -> RowChange for fast lookup."""
    return {change.key: change for change in result.changes}


def merge_results(
    base: DiffResult,
    overlay: DiffResult,
    prefer: str = "overlay",
) -> DiffResult:
    """Merge two DiffResults.

    When both results contain a change for the same key, ``prefer`` controls
    which one wins (``"overlay"`` or ``"base"``).

    Args:
        base:     The primary DiffResult.
        overlay:  The secondary DiffResult whose changes are merged in.
        prefer:   Which result wins on conflict (``"overlay"`` or ``"base"``).

    Returns:
        A new DiffResult containing the merged changes.

    Raises:
        ValueError: If ``prefer`` is not ``"overlay"`` or ``"base"``.
    """
    if prefer not in ("overlay", "base"):
        raise ValueError(f"prefer must be 'overlay' or 'base', got {prefer!r}")

    base_index = _index_changes(base)
    overlay_index = _index_changes(overlay)

    merged: Dict[str, RowChange] = {}

    # Start with all base changes
    for key, change in base_index.items():
        merged[key] = change

    # Apply overlay changes, respecting the conflict preference
    for key, change in overlay_index.items():
        if key not in merged:
            merged[key] = change
        else:
            if prefer == "overlay":
                merged[key] = change
            # else keep base — already in merged

    changes: List[RowChange] = list(merged.values())

    # Preserve column list from base, extending with any new columns from overlay
    seen = set(base.columns)
    extra = [c for c in overlay.columns if c not in seen]
    columns = base.columns + extra

    return DiffResult(changes=changes, columns=columns)


def merge_summary(result: DiffResult) -> Dict[str, int]:
    """Return a simple count summary of change types in a merged result."""
    counts: Dict[str, int] = {"added": 0, "removed": 0, "modified": 0}
    for change in result.changes:
        if change.change_type in counts:
            counts[change.change_type] += 1
    return counts
