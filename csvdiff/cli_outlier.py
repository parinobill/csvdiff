"""CLI sub-command: detect numeric outlier changes."""
from __future__ import annotations

import argparse
import json
import sys

from csvdiff.differ_outlier import OutlierResult, detect_outliers
from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff


def add_outlier_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "outliers",
        help="Detect rows whose numeric field changes are statistical outliers.",
    )
    p.add_argument("old_file", help="Original CSV file")
    p.add_argument("new_file", help="New CSV file")
    p.add_argument("--key", required=True, help="Key column name")
    p.add_argument(
        "--z-threshold",
        type=float,
        default=2.0,
        metavar="Z",
        help="Z-score threshold for outlier detection (default: 2.0)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    p.set_defaults(func=cmd_outlier)


def _render_json(result: OutlierResult) -> str:
    data = {
        "outlier_count": len(result.outliers),
        "field_stats": result.field_stats,
        "outliers": [
            {
                "key": o.change.key,
                "field": o.field_name,
                "old": o.old_value,
                "new": o.new_value,
                "delta": o.delta,
                "z_score": round(o.z_score, 4),
            }
            for o in result.outliers
        ],
    }
    return json.dumps(data, indent=2)


def cmd_outlier(args: argparse.Namespace) -> int:
    try:
        old_rows = read_csv(args.old_file, key_column=args.key)
        new_rows = read_csv(args.new_file, key_column=args.key)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    diff = compute_diff(old_rows, new_rows, key_column=args.key)
    result = detect_outliers(diff, z_threshold=args.z_threshold)

    if args.format == "json":
        print(_render_json(result))
    else:
        print(result.summary())

    return 1 if result.outliers else 0
