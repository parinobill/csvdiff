"""CLI sub-command: normalize — apply normalization rules to a CSV and print
or diff two CSVs after normalization.

Usage examples
--------------
  csvdiff normalize --strip --lowercase old.csv new.csv
  csvdiff normalize --value-map 'N/A=' --columns name,status old.csv new.csv
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from csvdiff.normalizer import NormalizeOptions, normalize_rows
from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff
from csvdiff.reporter import render_report


def add_normalize_args(subparsers) -> None:
    p = subparsers.add_parser(
        "normalize",
        help="Normalize field values then diff two CSV files.",
    )
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="New CSV file")
    p.add_argument("--key", default="id", help="Key column (default: id)")
    p.add_argument(
        "--strip",
        dest="strip_whitespace",
        action="store_true",
        default=True,
        help="Strip leading/trailing whitespace (default: on)",
    )
    p.add_argument(
        "--no-strip",
        dest="strip_whitespace",
        action="store_false",
        help="Disable whitespace stripping",
    )
    p.add_argument(
        "--lowercase",
        action="store_true",
        default=False,
        help="Lowercase all values before comparing",
    )
    p.add_argument(
        "--collapse-whitespace",
        action="store_true",
        default=False,
        help="Collapse internal whitespace runs to a single space",
    )
    p.add_argument(
        "--value-map",
        metavar="FROM=TO",
        action="append",
        default=[],
        help="Replace a specific value, e.g. 'N/A='.  Repeatable.",
    )
    p.add_argument(
        "--columns",
        metavar="COL1,COL2",
        default=None,
        help="Comma-separated list of columns to normalize (default: all)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    p.set_defaults(func=cmd_normalize)


def _parse_value_map(pairs: List[str]) -> dict:
    result = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"--value-map entry must be FROM=TO, got: {pair!r}"
            )
        frm, to = pair.split("=", 1)
        result[frm] = to
    return result


def cmd_normalize(args: argparse.Namespace) -> int:
    try:
        old_rows = read_csv(args.old, args.key)
        new_rows = read_csv(args.new, args.key)
    except (FileNotFoundError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    cols = [c.strip() for c in args.columns.split(",")] if args.columns else None
    opts = NormalizeOptions(
        strip_whitespace=args.strip_whitespace,
        lowercase=args.lowercase,
        collapse_whitespace=args.collapse_whitespace,
        value_map=_parse_value_map(args.value_map),
        columns=cols,
    )

    old_norm = normalize_rows(old_rows, opts)
    new_norm = normalize_rows(new_rows, opts)

    result = compute_diff(old_norm, new_norm, key_column=args.key)
    print(render_report(result, fmt=args.format))
    return 1 if result.has_changes() else 0
