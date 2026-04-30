"""CLI sub-command: watch-report — run N diff cycles and print a rolling report."""
from __future__ import annotations

import argparse
import sys
import time
from typing import List

from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff
from csvdiff.differ_watch_report import build_watch_report


def add_watch_report_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "watch-report",
        help="Repeatedly diff two files and emit a rolling change report.",
    )
    p.add_argument("file_a", help="Base CSV file")
    p.add_argument("file_b", help="Changed CSV file")
    p.add_argument("--key", required=True, help="Key column name")
    p.add_argument(
        "--cycles",
        type=int,
        default=3,
        help="Number of diff cycles to simulate (default: 3)",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=0.0,
        help="Seconds to wait between cycles (default: 0)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.set_defaults(func=cmd_watch_report)


def cmd_watch_report(args: argparse.Namespace) -> int:
    import json

    report = build_watch_report()

    for cycle_idx in range(args.cycles):
        try:
            rows_a = read_csv(args.file_a, key_column=args.key)
            rows_b = read_csv(args.file_b, key_column=args.key)
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        result = compute_diff(rows_a, rows_b, key_column=args.key)
        report.record(result, label=f"cycle-{cycle_idx + 1}")

        if cycle_idx < args.cycles - 1 and args.interval > 0:
            time.sleep(args.interval)

    if args.fmt == "json":
        data: List[dict] = []
        for entry in report.entries:
            data.append(
                {
                    "cycle": entry.cycle,
                    "label": entry.label,
                    "added": entry.stats.added,
                    "removed": entry.stats.removed,
                    "modified": entry.stats.modified,
                    "changed": entry.stats.changed,
                }
            )
        print(json.dumps(data, indent=2))
    else:
        print(report.summary())

    return 1 if (report.latest() and report.latest().stats.changed > 0) else 0  # type: ignore[union-attr]
