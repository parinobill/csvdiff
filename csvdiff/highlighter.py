"""Field-level diff highlighting for changed rows."""
from typing import Dict, List, Tuple
from csvdiff.differ import RowChange


def get_field_diffs(change: RowChange) -> List[Tuple[str, str, str]]:
    """Return list of (field, old_value, new_value) for changed fields."""
    if change.old is None or change.new is None:
        return []
    diffs = []
    all_keys = set(change.old) | set(change.new)
    for key in sorted(all_keys):
        old_val = change.old.get(key, "")
        new_val = change.new.get(key, "")
        if old_val != new_val:
            diffs.append((key, old_val, new_val))
    return diffs


def highlight_change(change: RowChange, use_color: bool = True) -> str:
    """Return a human-readable string highlighting changed fields."""
    diffs = get_field_diffs(change)
    if not diffs:
        return ""
    lines = [f"  Row key: {change.key}"]
    for field, old_val, new_val in diffs:
        if use_color:
            old_str = f"\033[31m{old_val}\033[0m"
            new_str = f"\033[32m{new_val}\033[0m"
        else:
            old_str = old_val
            new_str = new_val
        lines.append(f"    {field}: {old_str} -> {new_str}")
    return "\n".join(lines)


def highlight_all_changes(
    changes: List[RowChange], use_color: bool = True
) -> Dict[str, str]:
    """Return dict mapping row key to highlighted change string."""
    result = {}
    for change in changes:
        if change.change_type == "modified":
            result[change.key] = highlight_change(change, use_color=use_color)
    return result


def summarize_changes(changes: List[RowChange]) -> str:
    """Return a brief summary of added, removed, and modified row counts.

    Args:
        changes: List of RowChange objects from a diff operation.

    Returns:
        A single-line string summarising the counts, e.g.
        "added: 2, removed: 1, modified: 4"
    """
    counts: Dict[str, int] = {"added": 0, "removed": 0, "modified": 0}
    for change in changes:
        if change.change_type in counts:
            counts[change.change_type] += 1
    return ", ".join(f"{k}: {v}" for k, v in counts.items())
