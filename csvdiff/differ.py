"""Core diffing logic for csvdiff."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RowChange:
    key: str
    field: str
    old_value: Any
    new_value: Any

    def __str__(self) -> str:
        return f"  ~ [{self.key}] {self.field}: {self.old_value!r} -> {self.new_value!r}"


@dataclass
class DiffResult:
    added: list[dict] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)
    changed: list[RowChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        for row in self.added:
            lines.append(f"  + {row}")
        for row in self.removed:
            lines.append(f"  - {row}")
        for change in self.changed:
            lines.append(str(change))
        return "\n".join(lines) if lines else "No differences found."


def diff_csv(
    old_rows: list[dict],
    new_rows: list[dict],
    key_column: str,
) -> DiffResult:
    """Compare two lists of CSV row dicts by a key column."""
    result = DiffResult()

    old_by_key = {row[key_column]: row for row in old_rows}
    new_by_key = {row[key_column]: row for row in new_rows}

    old_keys = set(old_by_key)
    new_keys = set(new_by_key)

    for key in sorted(new_keys - old_keys):
        result.added.append(new_by_key[key])

    for key in sorted(old_keys - new_keys):
        result.removed.append(old_by_key[key])

    for key in sorted(old_keys & new_keys):
        old_row = old_by_key[key]
        new_row = new_by_key[key]
        all_fields = set(old_row) | set(new_row)
        for f in sorted(all_fields):
            if f == key_column:
                continue
            old_val = old_row.get(f)
            new_val = new_row.get(f)
            if old_val != new_val:
                result.changed.append(RowChange(key=key, field=f, old_value=old_val, new_value=new_val))

    return result
