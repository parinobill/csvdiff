"""CLI entry point for csvdiff."""
from __future__ import annotations
import argparse
import sys
from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff
from csvdiff.formatter import format_diff, format_summary
from csvdiff.reporter import render_report, OutputFormat


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff",
        description="Semantically diff two CSV files.",
    )
    p.add_argument("file_a", help="Original CSV file")
    p.add_argument("file_b", help="Modified CSV file")
    p.add_argument("-k", "--key", required=True, help="Column to use as row key")
    p.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json", "color"],
        default="color",
        help="Output format (default: color)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = read_csv(args.file_a, key_column=args.key)
        rows_b = read_csv(args.file_b, key_column=args.key)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = compute_diff(rows_a, rows_b, key_column=args.key)

    if args.fmt in ("text", "json"):
        print(render_report(result, fmt=args.fmt))
    else:
        use_color = not args.no_color
        print(format_diff(result, color=use_color))
        print(format_summary(result))

    return 1 if result.has_changes() else 0


if __name__ == "__main__":
    sys.exit(main())
