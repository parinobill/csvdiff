"""CLI sub-commands for baseline management."""

from __future__ import annotations

import argparse
import sys

from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff  # type: ignore[attr-defined]
from csvdiff.baseline import (
    save_baseline,
    load_baseline,
    diff_against_baseline,
    baseline_summary,
)
from csvdiff.formatter import format_diff


def add_baseline_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register 'baseline' sub-commands onto *subparsers*."""
    parent = subparsers.add_parser("baseline", help="Baseline management commands")
    sub = parent.add_subparsers(dest="baseline_cmd", required=True)

    # csvdiff baseline save <old> <new> --key id --output baseline.json
    p_save = sub.add_parser("save", help="Save current diff as a baseline")
    p_save.add_argument("old", help="Old CSV file")
    p_save.add_argument("new", help="New CSV file")
    p_save.add_argument("--key", required=True, help="Key column name")
    p_save.add_argument("--output", required=True, help="Path to write baseline JSON")
    p_save.set_defaults(func=cmd_save_baseline)

    # csvdiff baseline compare <old> <new> --key id --baseline baseline.json
    p_cmp = sub.add_parser("compare", help="Compare current diff against a saved baseline")
    p_cmp.add_argument("old", help="Old CSV file")
    p_cmp.add_argument("new", help="New CSV file")
    p_cmp.add_argument("--key", required=True, help="Key column name")
    p_cmp.add_argument("--baseline", required=True, help="Path to baseline JSON")
    p_cmp.add_argument("--no-color", action="store_true", help="Disable colour output")
    p_cmp.set_defaults(func=cmd_compare_baseline)


def cmd_save_baseline(args: argparse.Namespace) -> int:
    old_rows = read_csv(args.old, args.key)
    new_rows = read_csv(args.new, args.key)
    result = compute_diff(old_rows, new_rows, key_column=args.key)
    save_baseline(result, args.output)
    print(f"Baseline saved to {args.output} ({len(result.changes)} change(s) recorded).")
    return 0


def cmd_compare_baseline(args: argparse.Namespace) -> int:
    old_rows = read_csv(args.old, args.key)
    new_rows = read_csv(args.new, args.key)
    current = compute_diff(old_rows, new_rows, key_column=args.key)
    baseline = load_baseline(args.baseline)

    new_changes, resolved_changes = diff_against_baseline(current, baseline)
    print(baseline_summary(new_changes, resolved_changes))

    if new_changes:
        from csvdiff.differ import DiffResult
        new_result = DiffResult(key_column=args.key, changes=new_changes)
        color = not args.no_color
        print("\n--- New changes ---")
        print(format_diff(new_result, color=color))

    return 1 if new_changes else 0
