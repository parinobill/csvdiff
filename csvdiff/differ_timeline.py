"""Timeline diff: track how a key's fields changed across multiple DiffResults."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class TimelineEntry:
    """A single point-in-time snapshot of a row's field values."""
    label: str
    change_type: str  # 'added', 'removed', 'modified', 'unchanged'
    before: Optional[Dict[str, str]]
    after: Optional[Dict[str, str]]

    def __str__(self) -> str:
        return f"[{self.label}] {self.change_type}"


@dataclass
class RowTimeline:
    """All recorded changes for a single key value."""
    key_value: str
    entries: List[TimelineEntry] = field(default_factory=list)

    def add(self, entry: TimelineEntry) -> None:
        self.entries.append(entry)

    def field_history(self, column: str) -> List[Optional[str]]:
        """Return the value of *column* at each timeline entry (after-value)."""
        history: List[Optional[str]] = []
        for e in self.entries:
            if e.after is not None:
                history.append(e.after.get(column))
            elif e.before is not None:
                history.append(e.before.get(column))
            else:
                history.append(None)
        return history

    def __str__(self) -> str:
        lines = [f"Timeline for key={self.key_value!r}:"]
        for e in self.entries:
            lines.append(f"  {e}")
        return "\n".join(lines)


def build_timeline(
    labeled_results: List[tuple[str, DiffResult]],
) -> Dict[str, RowTimeline]:
    """Build a per-key timeline from an ordered list of (label, DiffResult) pairs.

    Args:
        labeled_results: Ordered sequence of (label, DiffResult). Labels are
            arbitrary strings such as dates or version tags.

    Returns:
        Mapping from key_value -> RowTimeline.
    """
    timelines: Dict[str, RowTimeline] = {}

    for label, result in labeled_results:
        for change in result.changes:
            key = change.key_value
            if key not in timelines:
                timelines[key] = RowTimeline(key_value=key)
            entry = TimelineEntry(
                label=label,
                change_type=change.change_type,
                before=change.before,
                after=change.after,
            )
            timelines[key].add(entry)

    return timelines


def timeline_summary(timelines: Dict[str, RowTimeline]) -> str:
    """Return a compact human-readable summary of all timelines."""
    if not timelines:
        return "No timeline data."
    lines = []
    for key, tl in sorted(timelines.items()):
        change_types = ", ".join(e.change_type for e in tl.entries)
        lines.append(f"{key}: {change_types}")
    return "\n".join(lines)
