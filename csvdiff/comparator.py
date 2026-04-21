"""Field-level comparison utilities with configurable tolerance for numeric and string fields."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CompareOptions:
    numeric_tolerance: float = 0.0
    case_sensitive: bool = True
    strip_whitespace: bool = True
    ignore_fields: list[str] = field(default_factory=list)


def _try_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def fields_equal(field_name: str, old: str, new: str, opts: CompareOptions) -> bool:
    """Return True if old and new should be considered equal under opts."""
    if field_name in opts.ignore_fields:
        return True

    if opts.strip_whitespace:
        old = old.strip()
        new = new.strip()

    if not opts.case_sensitive:
        old = old.lower()
        new = new.lower()

    if opts.numeric_tolerance > 0.0:
        old_f = _try_float(old)
        new_f = _try_float(new)
        if old_f is not None and new_f is not None:
            return abs(old_f - new_f) <= opts.numeric_tolerance

    return old == new


def compare_rows(
    key: str,
    old_row: dict[str, str],
    new_row: dict[str, str],
    opts: CompareOptions,
) -> dict[str, tuple[str, str]]:
    """Return a dict of field_name -> (old, new) for fields that differ."""
    all_fields = set(old_row) | set(new_row)
    diffs: dict[str, tuple[str, str]] = {}
    for f in all_fields:
        if f == key:
            continue
        old_val = old_row.get(f, "")
        new_val = new_row.get(f, "")
        if not fields_equal(f, old_val, new_val, opts):
            diffs[f] = (old_val, new_val)
    return diffs


def default_options() -> CompareOptions:
    return CompareOptions()
