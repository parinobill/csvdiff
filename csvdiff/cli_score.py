"""CLI sub-command: csvdiff score — print similarity score between two CSV files."""

import argparse
import json
import sys

from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff
from csvdiff.scorer import compute_score, score_as_dict


def add_score_args(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'score' sub-command on the given subparsers object."""
    parser = subparsers.add_parser(
        "score",
        help="Print a numeric similarity score between two CSV files.",
    )
    parser.add_argument("old_file", help="Path to the original CSV file.")
    parser.add_argument("new_file", help="Path to the updated CSV file.")
    parser.add_argument(
        "--key", required=True, metavar="COLUMN",
        help="Column to use as the unique row identifier.",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--threshold", type=float, default=None, metavar="0.0-1.0",
        help="Exit with code 1 if similarity score is below this threshold.",
    )
    parser.set_defaults(func=cmd_score)


def cmd_score(args: argparse.Namespace) -> int:
    """Execute the 'score' sub-command.

    Returns:
        Exit code (0 = success / above threshold, 1 = below threshold or error).
    """
    try:
        old_rows = read_csv(args.old_file, key_column=args.key)
        new_rows = read_csv(args.new_file, key_column=args.key)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = compute_diff(old_rows, new_rows, key_column=args.key)
    total_old = len(old_rows)
    score = compute_score(result, total_rows_in_old=total_old)

    if args.output_format == "json":
        print(json.dumps(score_as_dict(score), indent=2))
    else:
        print(str(score))

    if args.threshold is not None and score.score < args.threshold:
        print(
            f"Similarity {score.percent}% is below threshold "
            f"{args.threshold * 100:.2f}%.",
            file=sys.stderr,
        )
        return 1

    return 0
