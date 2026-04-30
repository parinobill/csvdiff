"""CLI sub-command: detect schema drift between two CSV files."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List

from csvdiff.parser import read_csv, get_all_columns
from csvdiff.differ_drift import detect_drift, SchemaDrift


def add_drift_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "drift",
        help="Detect schema drift (added/removed/reordered columns) between two CSV files.",
    )
    p.add_argument("old_file", help="Original CSV file")
    p.add_argument("new_file", help="New CSV file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.set_defaults(func=cmd_drift)


def _render_text(drift: SchemaDrift) -> str:
    lines: List[str] = [drift.summary()]
    if drift.reordered:
        lines.append(f"  Old order: {', '.join(drift.old_order)}")
        lines.append(f"  New order: {', '.join(drift.new_order)}")
    return "\n".join(lines)


def _render_json(drift: SchemaDrift) -> str:
    return json.dumps(drift.as_dict(), indent=2)


def cmd_drift(args: argparse.Namespace) -> int:
    try:
        old_rows = read_csv(args.old_file, key_column=None)  # type: ignore[arg-type]
        new_rows = read_csv(args.new_file, key_column=None)  # type: ignore[arg-type]
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    old_cols = get_all_columns(old_rows)
    new_cols = get_all_columns(new_rows)

    drift = detect_drift(old_cols, new_cols)

    if args.format == "json":
        print(_render_json(drift))
    else:
        print(_render_text(drift))

    return 1 if drift.has_drift else 0
