"""CLI sub-commands for snapshot capture and comparison."""
from __future__ import annotations

import argparse
import sys

from csvdiff.differ_snapshot import Snapshot, capture_snapshot, diff_snapshot
from csvdiff.formatter import format_diff, format_summary
from csvdiff.pipeline import PipelineOptions


def add_snapshot_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    # --- capture ---
    cap = subparsers.add_parser(
        "snapshot-capture",
        help="Capture a snapshot of a CSV file for later comparison.",
    )
    cap.add_argument("csv", help="Path to the CSV file to snapshot.")
    cap.add_argument("output", help="Path to write the snapshot JSON file.")
    cap.add_argument("--key", required=True, help="Key column name.")
    cap.add_argument("--label", default=None, help="Human-readable label for this snapshot.")
    cap.set_defaults(func=cmd_capture)

    # --- compare ---
    cmp = subparsers.add_parser(
        "snapshot-compare",
        help="Compare a saved snapshot against a current CSV file.",
    )
    cmp.add_argument("snapshot", help="Path to the snapshot JSON file.")
    cmp.add_argument("csv", help="Path to the current CSV file.")
    cmp.add_argument("--no-color", action="store_true", help="Disable ANSI colour output.")
    cmp.add_argument("--summary", action="store_true", help="Print summary line only.")
    cmp.set_defaults(func=cmd_compare)


def cmd_capture(args: argparse.Namespace) -> int:
    """Capture a snapshot and write it to *args.output*."""
    try:
        snap = capture_snapshot(args.csv, key_column=args.key, label=args.label)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    snap.save(args.output)
    print(
        f"Snapshot saved to {args.output!r}  "
        f"({snap.meta.row_count} rows, key='{snap.meta.key_column}')"
    )
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Compare a snapshot against the current CSV and print the diff."""
    try:
        snap = Snapshot.load(args.snapshot)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"error loading snapshot: {exc}", file=sys.stderr)
        return 1

    try:
        result = diff_snapshot(snap, args.csv)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    color = not args.no_color

    if args.summary:
        print(format_summary(result))
    else:
        output = format_diff(result, color=color)
        if output:
            print(output)
        else:
            print("No differences found.")

    return 1 if result.has_changes() else 0
