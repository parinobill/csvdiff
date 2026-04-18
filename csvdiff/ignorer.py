"""Ignore rules: skip rows or fields matching configured patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class IgnoreRules:
    columns: List[str] = field(default_factory=list)
    row_filter: Optional[str] = None  # regex applied to key value
    change_types: List[str] = field(default_factory=list)  # 'added','removed','modified'


def _matches_row_filter(change: RowChange, pattern: str) -> bool:
    return bool(re.search(pattern, change.key))


def apply_ignore(result: DiffResult, rules: IgnoreRules) -> DiffResult:
    """Return a new DiffResult with ignored changes/fields stripped out."""
    filtered: List[RowChange] = []

    for change in result.changes:
        if rules.change_types and change.change_type in rules.change_types:
            continue
        if rules.row_filter and _matches_row_filter(change, rules.row_filter):
            continue

        if rules.columns and change.change_type == "modified":
            new_fields: Dict[str, tuple] = {
                k: v
                for k, v in change.field_changes.items()
                if k not in rules.columns
            }
            if not new_fields:
                continue
            change = RowChange(
                key=change.key,
                change_type=change.change_type,
                field_changes=new_fields,
            )

        filtered.append(change)

    return DiffResult(changes=filtered, key_column=result.key_column)


def build_ignore_rules(
    ignore_columns: Optional[List[str]] = None,
    ignore_row_pattern: Optional[str] = None,
    ignore_change_types: Optional[List[str]] = None,
) -> IgnoreRules:
    return IgnoreRules(
        columns=ignore_columns or [],
        row_filter=ignore_row_pattern,
        change_types=ignore_change_types or [],
    )
