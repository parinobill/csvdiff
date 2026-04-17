"""Human-readable formatting of DiffResult objects."""

from typing import TextIO
import sys
from csvdiff.differ import DiffResult, RowChange


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if use_color:
        return f"{color}{text}{ANSI_RESET}"
    return text


def format_diff(result: DiffResult, use_color: bool = True, out: TextIO = sys.stdout) -> None:
    """Write a human-readable diff summary to `out`."""
    if not result.has_changes():
        out.write("No differences found.\n")
        return

    for key in result.added:
        row = result.added[key]
        line = f"+ [{key}] {dict(row)}\n"
        out.write(_colorize(line, ANSI_GREEN, use_color))

    for key in result.removed:
        row = result.removed[key]
        line = f"- [{key}] {dict(row)}\n"
        out.write(_colorize(line, ANSI_RED, use_color))

    for key, change in result.changed.items():
        out.write(_colorize(f"~ [{key}]\n", ANSI_YELLOW, use_color))
        for field, (old_val, new_val) in change.field_changes.items():
            out.write(f"    {field}: {old_val!r} -> {new_val!r}\n")


def format_summary(result: DiffResult, out: TextIO = sys.stdout) -> None:
    """Write a one-line summary of changes."""
    added = len(result.added)
    removed = len(result.removed)
    changed = len(result.changed)
    out.write(f"Summary: {added} added, {removed} removed, {changed} changed.\n")
