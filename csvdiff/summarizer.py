"""High-level summarizer combining stats with human-readable output."""
from typing import Optional
from csvdiff.differ import DiffResult
from csvdiff.stats import compute_stats, DiffStats


def _percent(part: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100 * part / total:.1f}%"


def summarize(result: DiffResult, total_rows: int = 0, verbose: bool = False) -> str:
    """Return a human-readable summary string for a diff result."""
    stats = compute_stats(result, total_rows)

    if stats.changed == 0:
        return "No differences found."

    lines = [f"Changes detected ({stats.changed} row(s) affected):"]
    if stats.added:
        lines.append(f"  + {stats.added} added   ({_percent(stats.added, total_rows)})")
    if stats.removed:
        lines.append(f"  - {stats.removed} removed ({_percent(stats.removed, total_rows)})")
    if stats.modified:
        lines.append(f"  ~ {stats.modified} modified ({_percent(stats.modified, total_rows)})")

    if verbose and total_rows:
        lines.append(f"  = {stats.unchanged} unchanged ({_percent(stats.unchanged, total_rows)})")
        lines.append(f"  Total rows compared: {total_rows}")

    return "\n".join(lines)


def summarize_stats(stats: DiffStats, verbose: bool = False) -> str:
    """Return a summary string directly from a DiffStats object."""
    from csvdiff.differ import DiffResult
    # Build a minimal proxy — reuse summarize logic via stats fields directly
    lines = []
    if stats.changed == 0:
        return "No differences found."
    lines.append(f"Changes detected ({stats.changed} row(s) affected):")
    if stats.added:
        lines.append(f"  + {stats.added} added")
    if stats.removed:
        lines.append(f"  - {stats.removed} removed")
    if stats.modified:
        lines.append(f"  ~ {stats.modified} modified")
    if verbose:
        lines.append(f"  = {stats.unchanged} unchanged")
    return "\n".join(lines)
