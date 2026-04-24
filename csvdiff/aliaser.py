"""Column aliasing: rename columns in diff output using a mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class AliasMap:
    """Bidirectional mapping between original and display column names."""

    mapping: Dict[str, str] = field(default_factory=dict)

    def display(self, column: str) -> str:
        """Return display name for *column*, falling back to the original."""
        return self.mapping.get(column, column)

    def reverse(self) -> "AliasMap":
        """Return an AliasMap with source and target swapped."""
        return AliasMap({v: k for k, v in self.mapping.items()})

    def apply_to_dict(self, row: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of *row* with keys renamed according to the mapping."""
        return {self.display(k): v for k, v in row.items()}


def _alias_change(change: RowChange, alias: AliasMap) -> RowChange:
    """Return a new RowChange with column names replaced by their aliases."""
    return RowChange(
        change_type=change.change_type,
        key=change.key,
        old_row=alias.apply_to_dict(change.old_row) if change.old_row else None,
        new_row=alias.apply_to_dict(change.new_row) if change.new_row else None,
        changed_fields=[
            (alias.display(col), old, new)
            for col, old, new in (change.changed_fields or [])
        ],
    )


def alias_diff(result: DiffResult, alias: AliasMap) -> DiffResult:
    """Return a new DiffResult with all column names replaced by their aliases."""
    aliased_changes = [_alias_change(c, alias) for c in result.changes]
    return DiffResult(
        changes=aliased_changes,
        unchanged_count=result.unchanged_count,
    )


def build_alias_map(pairs: List[str]) -> AliasMap:
    """Build an AliasMap from a list of ``original:alias`` strings.

    Raises ``ValueError`` for malformed entries.
    """
    mapping: Dict[str, str] = {}
    for pair in pairs:
        if ":" not in pair:
            raise ValueError(
                f"Invalid alias specification {pair!r}: expected 'original:alias'"
            )
        original, _, alias = pair.partition(":")
        original, alias = original.strip(), alias.strip()
        if not original or not alias:
            raise ValueError(
                f"Invalid alias specification {pair!r}: both sides must be non-empty"
            )
        mapping[original] = alias
    return AliasMap(mapping)
