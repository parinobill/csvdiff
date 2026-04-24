"""Normalize field values in CSV rows before diffing.

Supports stripping whitespace, lowercasing, collapsing internal
whitespace, and custom value mappings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class NormalizeOptions:
    strip_whitespace: bool = True
    lowercase: bool = False
    collapse_whitespace: bool = False
    value_map: Dict[str, str] = field(default_factory=dict)
    columns: Optional[List[str]] = None  # None means all columns


def _normalize_value(value: str, opts: NormalizeOptions) -> str:
    if opts.strip_whitespace:
        value = value.strip()
    if opts.collapse_whitespace:
        value = re.sub(r"\s+", " ", value)
    if opts.lowercase:
        value = value.lower()
    if value in opts.value_map:
        value = opts.value_map[value]
    return value


def normalize_row(
    row: Dict[str, str],
    opts: NormalizeOptions,
) -> Dict[str, str]:
    """Return a new row dict with normalized values."""
    result = {}
    for col, val in row.items():
        if opts.columns is None or col in opts.columns:
            result[col] = _normalize_value(val, opts)
        else:
            result[col] = val
    return result


def normalize_rows(
    rows: List[Dict[str, str]],
    opts: NormalizeOptions,
) -> List[Dict[str, str]]:
    """Normalize all rows in a list."""
    return [normalize_row(row, opts) for row in rows]


def default_options() -> NormalizeOptions:
    return NormalizeOptions()


def options_from_dict(d: dict) -> NormalizeOptions:
    """Build NormalizeOptions from a plain dict (e.g. loaded from config)."""
    return NormalizeOptions(
        strip_whitespace=d.get("strip_whitespace", True),
        lowercase=d.get("lowercase", False),
        collapse_whitespace=d.get("collapse_whitespace", False),
        value_map=d.get("value_map", {}),
        columns=d.get("columns", None),
    )
