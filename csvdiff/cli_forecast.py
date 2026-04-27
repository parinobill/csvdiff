"""CLI subcommand: forecast change trends from a ledger file."""
from __future__ import annotations

import argparse
import json
import sys

from csvdiff.audit_store import load_entries
from csvdiff.differ_forecast import forecast_from_ledger, ForecastResult


def add_forecast_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "forecast",
        help="Forecast future change counts from ledger history",
    )
    p.add_argument("ledger", help="Path to the ledger JSONL file")
    p.add_argument(
        "--steps",
        type=int,
        default=3,
        metavar="N",
        help="Number of future runs to forecast (default: 3)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format",
    )
    p.set_defaults(func=cmd_forecast)


def _render_json(result: ForecastResult) -> str:
    data = {
        "trend": {
            "added": round(result.trend_added, 4),
            "removed": round(result.trend_removed, 4),
            "modified": round(result.trend_modified, 4),
        },
        "forecast": [
            {
                "run_index": p.run_index,
                "added": round(p.predicted_added, 2),
                "removed": round(p.predicted_removed, 2),
                "modified": round(p.predicted_modified, 2),
                "total": round(p.predicted_total, 2),
            }
            for p in result.points
        ],
    }
    return json.dumps(data, indent=2)


def cmd_forecast(args: argparse.Namespace) -> int:
    try:
        entries = load_entries(args.ledger)
    except FileNotFoundError:
        print(f"Error: ledger file not found: {args.ledger}", file=sys.stderr)
        return 1

    if not entries:
        print("No ledger entries found; cannot forecast.", file=sys.stderr)
        return 1

    result = forecast_from_ledger(entries, steps=args.steps)

    if args.fmt == "json":
        print(_render_json(result))
    else:
        print(result.summary())

    return 0
