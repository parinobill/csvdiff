"""CLI sub-command: threshold — filter a diff by significance thresholds."""
from __future__ import annotations

import argparse
import sys

from csvdiff.differ import DiffResult
from csvdiff.differ_threshold import ThresholdOptions, apply_threshold
from csvdiff.pipeline import PipelineOptions, run_pipeline
from csvdiff.formatter import format_diff, format_summary


def add_threshold_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "threshold",
        help="Suppress changes that do not meet significance thresholds.",
    )
    p.add_argument("old", help="Original CSV file.")
    p.add_argument("new", help="Updated CSV file.")
    p.add_argument("--key", required=True, help="Key column name.")
    p.add_argument(
        "--min-changed-fields",
        type=int,
        default=1,
        metavar="N",
        help="Minimum number of changed fields for a modified row to be kept (default: 1).",
    )
    p.add_argument(
        "--max-pct-added",
        type=float,
        default=None,
        metavar="PCT",
        help="Suppress entire diff if added rows exceed PCT%% of total.",
    )
    p.add_argument(
        "--max-pct-removed",
        type=float,
        default=None,
        metavar="PCT",
        help="Suppress entire diff if removed rows exceed PCT%% of total.",
    )
    p.add_argument(
        "--require-min-rows",
        type=int,
        default=0,
        metavar="N",
        help="Suppress diff when total rows (old+new) is below N.",
    )
    p.add_argument("--no-color", action="store_true", help="Disable colour output.")
    p.set_defaults(func=cmd_threshold)


def cmd_threshold(args: argparse.Namespace) -> int:
    popts = PipelineOptions(key_column=args.key)
    result: DiffResult = run_pipeline(args.old, args.new, popts)

    topts = ThresholdOptions(
        min_changed_fields=args.min_changed_fields,
        max_pct_added=args.max_pct_added,
        max_pct_removed=args.max_pct_removed,
        require_min_rows=args.require_min_rows,
    )
    tres = apply_threshold(result, topts)

    if tres.suppressed:
        print(tres.summary())
        return 0

    filtered = DiffResult(changes=tres.kept)
    color = not getattr(args, "no_color", False)
    print(format_diff(filtered, color=color))
    print(format_summary(filtered))
    print(tres.summary())
    return 1 if tres.kept else 0
