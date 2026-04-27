"""CLI sub-command: rank changes by a numeric field."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from csvdiff.differ import DiffResult
from csvdiff.differ_rank import rank_diff, RankedChange


def add_rank_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "rank",
        help="Rank diff changes by the numeric delta of a chosen field.",
    )
    p.add_argument("field", help="CSV field name to rank by (must be numeric).")
    p.add_argument(
        "--top", "-n",
        type=int,
        default=None,
        metavar="N",
        help="Show only the top N changes (default: all).",
    )
    p.add_argument(
        "--asc",
        action="store_true",
        default=False,
        help="Sort ascending instead of descending.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.set_defaults(func=cmd_rank)


def _render_text(ranked: List[RankedChange], rank_field: str) -> str:
    if not ranked:
        return "No changes to rank."
    lines = [f"Ranked by '{rank_field}' (top {len(ranked)}):"]
    for rc in ranked:
        lines.append(f"  #{rc.rank:>3}  score={rc.score:>12.4f}  key={rc.change.key}  type={rc.change.change_type}")
    return "\n".join(lines)


def _render_json(ranked: List[RankedChange], rank_field: str) -> str:
    records = [
        {
            "rank": rc.rank,
            "score": rc.score,
            "key": rc.change.key,
            "change_type": rc.change.change_type,
            "rank_field": rank_field,
        }
        for rc in ranked
    ]
    return json.dumps(records, indent=2)


def cmd_rank(args: argparse.Namespace, result: DiffResult) -> int:
    """Entry point called by the main CLI dispatcher."""
    try:
        rank_result = rank_diff(
            result,
            rank_field=args.field,
            top_n=args.top,
            ascending=args.asc,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    visible = rank_result.top()

    if args.format == "json":
        print(_render_json(visible, args.field))
    else:
        print(_render_text(visible, args.field))

    return 0 if not visible else 1
