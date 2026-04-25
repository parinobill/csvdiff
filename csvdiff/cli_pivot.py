"""CLI sub-command: pivot — show changes grouped by field name."""
from __future__ import annotations

import argparse
import sys

from csvdiff.differ import DiffResult
from csvdiff.differ_pivot import FieldPivot, top_changed_fields


def add_pivot_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "pivot",
        help="Show diff results pivoted by field name.",
    )
    p.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="Show only the top N most-changed fields.",
    )
    p.add_argument(
        "--format",
        choices=["text", "csv"],
        default="text",
        dest="pivot_format",
        help="Output format (default: text).",
    )
    p.set_defaults(pivot_func=cmd_pivot)


def _render_text(pivots: list[FieldPivot]) -> str:
    if not pivots:
        return "No field changes found."
    lines = ["Field pivot summary:", ""]
    for pv in pivots:
        lines.append(f"  {pv.summary()}")
    return "\n".join(lines)


def _render_csv(pivots: list[FieldPivot]) -> str:
    lines = ["field,added,removed,modified"]
    for pv in pivots:
        lines.append(
            f"{pv.field_name},{len(pv.added_values)},{len(pv.removed_values)},{len(pv.old_values)}"
        )
    return "\n".join(lines)


def cmd_pivot(args: argparse.Namespace, result: DiffResult) -> int:
    """Execute the pivot command.  Returns exit code."""
    pivots = top_changed_fields(result, n=args.top)

    if args.pivot_format == "csv":
        print(_render_csv(pivots))
    else:
        print(_render_text(pivots))

    return 0 if not result.has_changes() else 1
