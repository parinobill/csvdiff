"""CLI sub-command: rebase a patch against an upstream diff."""

import argparse
import sys

from csvdiff.patch_io import load_patch, save_patch
from csvdiff.differ_patch import Patch
from csvdiff.differ_rebase import rebase_patch, rebase_summary


def add_rebase_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "rebase",
        help="Rebase a patch on top of an upstream patch to resolve conflicts",
    )
    p.add_argument("original", help="Path to the original patch JSON")
    p.add_argument("upstream", help="Path to the upstream patch JSON")
    p.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write rebased patch to this file (default: stdout)",
    )
    p.add_argument(
        "--fail-on-conflicts",
        action="store_true",
        help="Exit with code 2 if any conflicts are detected",
    )
    p.set_defaults(func=cmd_rebase)


def cmd_rebase(args: argparse.Namespace) -> int:
    try:
        orig_patch = load_patch(args.original)
        up_patch = load_patch(args.upstream)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    orig_result = orig_patch.to_diff_result()
    up_result = up_patch.to_diff_result()

    rebase_result = rebase_patch(orig_result, up_result)

    print(rebase_summary(rebase_result), file=sys.stderr)

    rebased_patch = Patch.from_diff_result(rebase_result.rebased)

    if args.output:
        save_patch(rebased_patch, args.output)
    else:
        print(rebased_patch.to_json())

    if args.fail_on_conflicts and rebase_result.has_conflicts:
        return 2

    return 0
