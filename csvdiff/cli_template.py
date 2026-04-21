"""CLI sub-commands for template-based report generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff  # type: ignore[attr-defined]
from csvdiff.templater import list_builtin_formats, render_template


def add_template_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'template' sub-command."""
    p = subparsers.add_parser(
        "template",
        help="Render a diff report using a text/HTML template.",
    )
    p.add_argument("file_a", help="Original CSV file.")
    p.add_argument("file_b", help="New CSV file.")
    p.add_argument("--key", default="id", help="Key column name (default: id).")
    p.add_argument(
        "--format",
        dest="fmt",
        choices=list_builtin_formats(),
        default="text",
        help="Built-in template format (default: text).",
    )
    p.add_argument(
        "--template-file",
        dest="template_file",
        default=None,
        help="Path to a custom Template file (overrides --format).",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    p.set_defaults(func=cmd_template)


def cmd_template(args: argparse.Namespace) -> int:
    """Execute the template sub-command."""
    try:
        rows_a = read_csv(args.file_a, key_column=args.key)
        rows_b = read_csv(args.file_b, key_column=args.key)
    except (FileNotFoundError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = compute_diff(rows_a, rows_b, key_column=args.key)

    template_str: str | None = None
    if args.template_file:
        try:
            template_str = Path(args.template_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Error reading template file: {exc}", file=sys.stderr)
            return 1

    rendered = render_template(
        result,
        file_a=args.file_a,
        file_b=args.file_b,
        template_str=template_str,
        fmt=args.fmt,
    )

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(rendered)

    return 1 if result.has_changes() else 0
