"""CLI sub-command: profile — show per-column change statistics."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff  # type: ignore[attr-defined]
from csvdiff.profiler import profile_diff


def add_profile_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *profile* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "profile",
        help="Show per-column change statistics for two CSV files.",
    )
    p.add_argument("file_a", help="Original CSV file")
    p.add_argument("file_b", help="Modified CSV file")
    p.add_argument("-k", "--key", default="id", help="Key column name (default: id)")
    p.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Show top N most-changed columns (default: 5)",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output profile as JSON",
    )
    p.set_defaults(func=cmd_profile)


def cmd_profile(args: argparse.Namespace) -> int:
    """Execute the profile sub-command; returns an exit code."""
    try:
        rows_a = read_csv(args.file_a, key_column=args.key)
        rows_b = read_csv(args.file_b, key_column=args.key)
    except (FileNotFoundError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = compute_diff(rows_a, rows_b, key_column=args.key)
    prof = profile_diff(result)

    if args.as_json:
        data = {
            "total_rows_affected": prof.total_rows_affected,
            "added": prof.added,
            "removed": prof.removed,
            "modified": prof.modified,
            "top_columns": [
                {"column": cp.column, "change_count": cp.change_count}
                for cp in prof.most_changed_columns(args.top)
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(
            f"Rows affected : {prof.total_rows_affected} "
            f"(+{prof.added} added, -{prof.removed} removed, ~{prof.modified} modified)"
        )
        top = prof.most_changed_columns(args.top)
        if top:
            print(f"\nTop {args.top} most-changed columns:")
            for cp in top:
                print(f"  {cp.summary}")
        else:
            print("No column-level changes detected.")

    return 0
