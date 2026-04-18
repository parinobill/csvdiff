"""CLI entry point for csvdiff."""
import sys
import argparse
from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff
from csvdiff.reporter import render_report
from csvdiff.filter import filter_columns


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff",
        description="Semantically diff two CSV files.",
    )
    p.add_argument("file_a", help="Original CSV file")
    p.add_argument("file_b", help="Modified CSV file")
    p.add_argument("--key", required=True, help="Column to use as row identifier")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.add_argument("--include-columns", nargs="+", metavar="COL", default=None,
                   help="Only diff these columns")
    p.add_argument("--exclude-columns", nargs="+", metavar="COL", default=None,
                   help="Exclude these columns from diff")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = read_csv(args.file_a, args.key)
        rows_b = read_csv(args.file_b, args.key)
    except (FileNotFoundError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.include_columns or args.exclude_columns:
        rows_a = filter_columns(rows_a, include=args.include_columns, exclude=args.exclude_columns)
        rows_b = filter_columns(rows_b, include=args.include_columns, exclude=args.exclude_columns)

    result = compute_diff(rows_a, rows_b, args.key)
    print(render_report(result, fmt=args.fmt))
    return 1 if result.has_changes() else 0


if __name__ == "__main__":
    sys.exit(main())
