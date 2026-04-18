"""CLI entry point for csvdiff."""

import argparse
import sys

from csvdiff.differ import compute_diff
from csvdiff.exporter import export_csv, export_json, export_markdown
from csvdiff.parser import read_csv
from csvdiff.reporter import render_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff",
        description="Semantically diff two CSV files.",
    )
    p.add_argument("file_a", help="Original CSV file")
    p.add_argument("file_b", help="Modified CSV file")
    p.add_argument("--key", required=True, help="Column to use as row identifier")
    p.add_argument(
        "--format",
        choices=["text", "json", "csv", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = read_csv(args.file_a, key_column=args.key)
        rows_b = read_csv(args.file_b, key_column=args.key)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = compute_diff(rows_a, rows_b, key_column=args.key)

    if args.format == "json":
        print(export_json(result))
    elif args.format == "csv":
        print(export_csv(result), end="")
    elif args.format == "markdown":
        print(export_markdown(result), end="")
    else:
        print(render_report(result, color=not args.no_color))

    return 1 if result.has_changes() else 0


if __name__ == "__main__":
    sys.exit(main())
