"""CLI sub-command: compare two CSV files with tolerance options."""

from __future__ import annotations

import argparse
import sys

from csvdiff.comparator import CompareOptions, compare_rows
from csvdiff.parser import read_csv


def add_compare_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "compare",
        help="Compare two CSV files with configurable field-level tolerance.",
    )
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="Updated CSV file")
    p.add_argument("--key", default="id", help="Key column name (default: id)")
    p.add_argument(
        "--numeric-tolerance",
        type=float,
        default=0.0,
        metavar="TOL",
        help="Allowed absolute difference for numeric fields (default: 0)",
    )
    p.add_argument(
        "--case-insensitive",
        action="store_true",
        help="Ignore case when comparing string fields",
    )
    p.add_argument(
        "--no-strip",
        action="store_true",
        help="Do not strip surrounding whitespace before comparing",
    )
    p.add_argument(
        "--ignore-fields",
        nargs="*",
        default=[],
        metavar="FIELD",
        help="Field names to ignore during comparison",
    )
    p.set_defaults(func=cmd_compare)


def cmd_compare(args: argparse.Namespace) -> int:
    try:
        old_rows = read_csv(args.old, args.key)
        new_rows = read_csv(args.new, args.key)
    except (FileNotFoundError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    opts = CompareOptions(
        numeric_tolerance=args.numeric_tolerance,
        case_sensitive=not args.case_insensitive,
        strip_whitespace=not args.no_strip,
        ignore_fields=list(args.ignore_fields),
    )

    all_keys = set(old_rows) | set(new_rows)
    differences: list[tuple[str, dict[str, tuple[str, str]]]] = []

    for key in sorted(all_keys):
        if key not in old_rows:
            print(f"+ [{key}] (added)")
            differences.append((key, {}))
        elif key not in new_rows:
            print(f"- [{key}] (removed)")
            differences.append((key, {}))
        else:
            diffs = compare_rows(args.key, old_rows[key], new_rows[key], opts)
            if diffs:
                print(f"~ [{key}]")
                for field_name, (old_val, new_val) in sorted(diffs.items()):
                    print(f"    {field_name}: {old_val!r} -> {new_val!r}")
                differences.append((key, diffs))

    if not differences:
        print("No differences found.")
        return 0

    print(f"\n{len(differences)} row(s) differ.")
    return 1
