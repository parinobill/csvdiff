"""Core diffing logic for csvdiff."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RowChange:
    key: str
    change_type: str  # 'added', 'removed', 'modified'
    old: Optional[Dict[str, str]] = None
    new: Optional[Dict[str, str]] = None

    def __str__(self) -> str:
        return f"[{self.change_type.upper()}] key={self.key}"


@dataclass
class DiffResult:
    changes: List[RowChange] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        added = sum(1 for c in self.changes if c.change_type == "added")
        removed = sum(1 for c in self.changes if c.change_type == "removed")
        modified = sum(1 for c in self.changes if c.change_type == "modified")
        return f"+{added} added, -{removed} removed, ~{modified} modified"

    def by_type(self, change_type: str) -> List[RowChange]:
        return [c for c in self.changes if c.change_type == change_type]


def diff_csv(
    old_rows: List[Dict[str, str]],
    new_rows: List[Dict[str, str]],
    key_column: str,
) -> DiffResult:
    """Diff two lists of CSV row dicts by key column."""
    old_map = {row[key_column]: row for row in old_rows}
    new_map = {row[key_column]: row for row in new_rows}

    changes: List[RowChange] = []

    for key, old_row in old_map.items():
        if key not in new_map:
            changes.append(RowChange(key=key, change_type="removed", old=old_row))
        elif old_row != new_map[key]:
            changes.append(
                RowChange(key=key, change_type="modified", old=old_row, new=new_map[key])
            )

    for key, new_row in new_map.items():
        if key not in old_map:
            changes.append(RowChange(key=key, change_type="added", new=new_row))

    return DiffResult(changes=changes)
