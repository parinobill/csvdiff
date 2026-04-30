"""CLI sub-command: variance — show which fields change most in a diff."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from csvdiff.differ_variance import FieldVariance, VarianceResult, compute_variance
from csvdiff.pipeline import PipelineOptions, run_pipeline


def add_variance_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "variance",
        help="Show which fields vary most between two CSV files.",
    )
    p.add_argument("old_file", help="Original CSV file")
    p.add_argument("new_file", help="Updated CSV file")
    p.add_argument("--key", required=True, help="Key column name")
    p.add_argument(
        "--top",
        type=int,
        default=10,
        metavar="N",
        help="Show top N fields by change count (default: 10)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    p.set_defaults(func=cmd_variance)


def _render_text(vr: VarianceResult, top: int) -> str:
    entries = vr.top(top)
    if not entries:
        return "No field variance detected."
    lines = ["Field variance:"]
    for fv in entries:
        lines.append(f"  {fv.summary()}")
    return "\n".join(lines)


def _render_json(vr: VarianceResult, top: int) -> str:
    entries = vr.top(top)
    out = []
    for fv in entries:
        record = {
            "field": fv.field_name,
            "change_count": fv.change_count,
            "mean_delta": fv.mean_delta,
            "max_delta": fv.max_delta,
        }
        out.append(record)
    return json.dumps(out, indent=2)


def cmd_variance(args: argparse.Namespace) -> int:
    opts = PipelineOptions(key_column=args.key)
    try:
        diff_result = run_pipeline(args.old_file, args.new_file, opts)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    vr = compute_variance(diff_result)

    if args.output_format == "json":
        print(_render_json(vr, args.top))
    else:
        print(_render_text(vr, args.top))

    return 0 if not vr.fields else 1
