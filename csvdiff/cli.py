"""CLI entry point for csvdiff."""

import argparse
import sys
from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff
from csvdiff.formatter import format_diff, format_summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff",
        description="Semantically diff two CSV files.",
    )
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="Updated CSV file")
    p.add_argument("-k", "--key", required=True, help="Column to use as row key")
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    p.add_argument("--summary", action="store_true", help="Print summary line")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        old_rows = read_csv(args.old, key_column=args.key)
        new_rows = read_csv(args.new, key_column=args.key)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = compute_diff(old_rows, new_rows)
    use_color = not args.no_color
    format_diff(result, use_color=use_color)

    if args.summary:
        format_summary(result)

    return 0 if not result.has_changes() else 1


if __name__ == "__main__":
    sys.exit(main())
