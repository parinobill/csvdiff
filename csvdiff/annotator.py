"""Annotate diff changes with contextual metadata (row index, severity, tags)."""

from dataclasses import dataclass, field
from typing import List, Optional
from csvdiff.differ import RowChange, DiffResult


@dataclass
class AnnotatedChange:
    change: RowChange
    row_index: Optional[int] = None
    severity: str = "info"
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        parts = [f"[{self.severity.upper()}]"]
        if self.row_index is not None:
            parts.append(f"row={self.row_index}")
        if self.tags:
            parts.append(f"tags={','.join(self.tags)}")
        parts.append(str(self.change))
        return " ".join(parts)


def _severity_for(change: RowChange) -> str:
    if change.change_type == "removed":
        return "warning"
    if change.change_type == "added":
        return "info"
    return "notice"


def _tags_for(change: RowChange, key_column: str) -> List[str]:
    tags = [change.change_type]
    if change.change_type == "modified" and change.field_changes:
        tags.append(f"fields:{len(change.field_changes)}")
    return tags


def annotate_changes(
    result: DiffResult,
    key_column: str,
    index_map: Optional[dict] = None,
) -> List[AnnotatedChange]:
    """Return annotated versions of all changes in a DiffResult."""
    annotated = []
    for change in result.changes:
        row_idx = None
        if index_map:
            row_idx = index_map.get(change.key)
        annotated.append(
            AnnotatedChange(
                change=change,
                row_index=row_idx,
                severity=_severity_for(change),
                tags=_tags_for(change, key_column),
            )
        )
    return annotated
