"""Tag changes with user-defined or auto-generated labels for categorization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


@dataclass
class TagRule:
    """A rule that assigns a tag when a condition is met."""

    tag: str
    change_type: Optional[str] = None   # 'added', 'removed', 'modified', or None for any
    field_name: Optional[str] = None    # only for modified rows
    field_value: Optional[str] = None   # match old or new value substring

    def matches(self, change: RowChange) -> bool:
        if self.change_type and change.change_type != self.change_type:
            return False
        if self.field_name and change.change_type == "modified":
            diffs = change.field_diffs or {}
            if self.field_name not in diffs:
                return False
            if self.field_value:
                old, new = diffs[self.field_name]
                if self.field_value not in str(old) and self.field_value not in str(new):
                    return False
        elif self.field_name and change.change_type != "modified":
            return False
        return True


@dataclass
class TaggedChange:
    change: RowChange
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag_str = ", ".join(self.tags) if self.tags else "(none)"
        return f"{self.change} [tags: {tag_str}]"


def apply_tags(result: DiffResult, rules: List[TagRule]) -> List[TaggedChange]:
    """Apply tag rules to all changes and return TaggedChange objects."""
    tagged: List[TaggedChange] = []
    for change in result.changes:
        matched = [rule.tag for rule in rules if rule.matches(change)]
        tagged.append(TaggedChange(change=change, tags=matched))
    return tagged


def group_by_tag(tagged_changes: List[TaggedChange]) -> Dict[str, List[TaggedChange]]:
    """Group TaggedChange objects by tag. Untagged changes appear under ''."""
    groups: Dict[str, List[TaggedChange]] = {}
    for tc in tagged_changes:
        if not tc.tags:
            groups.setdefault("", []).append(tc)
        for tag in tc.tags:
            groups.setdefault(tag, []).append(tc)
    return groups


def tag_summary(tagged_changes: List[TaggedChange]) -> str:
    """Return a human-readable summary of tag distribution."""
    groups = group_by_tag(tagged_changes)
    if not groups:
        return "No changes to tag."
    lines = [f"Tag distribution ({len(tagged_changes)} change(s)):"]
    for tag, items in sorted(groups.items()):
        label = tag if tag else "(untagged)"
        lines.append(f"  {label}: {len(items)}")
    return "\n".join(lines)
