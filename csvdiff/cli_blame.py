"""CLI sub-command: blame — show which diff version introduced each change."""
from __future__ import annotations

import argparse
import sys
from typing import List, Tuple

from csvdiff.differ import DiffResult
from csvdiff.differ_blame import blame_changes, BlameResult
from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff  # type: ignore[attr-defined]


def add_blame_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "blame",
        help="Attribute each change to the earliest CSV version that introduced it.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more CSV files in chronological order (oldest first).",
    )
    p.add_argument("--key", required=True, help="Column to use as the row key.")
    p.add_argument(
        "--json", action="store_true", default=False, help="Output blame as JSON."
    )
    p.set_defaults(func=cmd_blame)


def _build_labeled_results(
    files: List[str], key_column: str
) -> List[Tuple[str, DiffResult]]:
    labeled: List[Tuple[str, DiffResult]] = []
    prev_rows = read_csv(files[0], key_column)
    for path in files[1:]:
        curr_rows = read_csv(path, key_column)
        result = compute_diff(prev_rows, curr_rows, key_column)
        label = f"{files[files.index(path) - 1]} → {path}"
        labeled.append((label, result))
        prev_rows = curr_rows
    return labeled


def _render_text(br: BlameResult) -> str:
    if not br.blamed:
        return "No changes found across all versions.\n"
    lines = []
    for b in br.blamed:
        lines.append(str(b))
    lines.append("")
    lines.append(br.summary())
    return "\n".join(lines)


def cmd_blame(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("blame requires at least two files.", file=sys.stderr)
        return 1

    try:
        labeled = _build_labeled_results(args.files, args.key)
    except (FileNotFoundError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    br = blame_changes(labeled)

    if args.json:
        import json

        data = [
            {
                "source": b.source_label,
                "change_type": b.change.change_type,
                "key": b.change.key_value,
            }
            for b in br.blamed
        ]
        print(json.dumps(data, indent=2))
    else:
        print(_render_text(br), end="")

    return 1 if br.blamed else 0
