"""CLI sub-commands: generate-patch and apply-patch."""
from __future__ import annotations
import argparse
import sys
from typing import List

from csvdiff.parser import read_csv
from csvdiff.differ import compute_diff
from csvdiff.differ_patch import build_patch, apply_patch
from csvdiff.patch_io import save_patch, load_patch, patch_summary


def add_patch_commands(subparsers) -> None:
    gen = subparsers.add_parser("generate-patch", help="Generate a patch file from two CSVs")
    gen.add_argument("old_file")
    gen.add_argument("new_file")
    gen.add_argument("--key", required=True, help="Key column name")
    gen.add_argument("--output", "-o", required=True, help="Output patch JSON file")
    gen.set_defaults(func=cmd_generate_patch)

    apl = subparsers.add_parser("apply-patch", help="Apply a patch file to a CSV")
    apl.add_argument("input_file")
    apl.add_argument("patch_file")
    apl.add_argument("--output", "-o", required=True, help="Output CSV file")
    apl.set_defaults(func=cmd_apply_patch)


def cmd_generate_patch(args) -> int:
    try:
        old_rows = read_csv(args.old_file, args.key)
        new_rows = read_csv(args.new_file, args.key)
    except (FileNotFoundError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = compute_diff(old_rows, new_rows, args.key)
    patch = build_patch(result, args.key)
    save_patch(patch, args.output)
    print(patch_summary(patch))
    return 0


def cmd_apply_patch(args) -> int:
    try:
        patch = load_patch(args.patch_file)
        rows = read_csv(args.input_file, patch.key_column)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    patched = apply_patch(list(rows.values()), patch)

    import csv, io
    if not patched:
        print("No rows in output.", file=sys.stderr)
        return 0

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(patched[0].keys()))
        writer.writeheader()
        writer.writerows(patched)

    print(f"Written {len(patched)} rows to {args.output}")
    return 0
