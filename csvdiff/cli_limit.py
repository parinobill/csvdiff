"""CLI helpers for the --limit family of flags."""

import argparse
from typing import Optional

from csvdiff.differ import DiffResult
from csvdiff.limiter import LimitOptions, limit_diff, limit_summary


def add_limit_args(parser: argparse.ArgumentParser) -> None:
    """Attach limit-related arguments to *parser*."""
    grp = parser.add_argument_group("output limits")
    grp.add_argument(
        "--max-changes",
        type=int,
        default=None,
        metavar="N",
        help="Cap total number of reported changes to N.",
    )
    grp.add_argument(
        "--max-added",
        type=int,
        default=None,
        metavar="N",
        help="Cap the number of reported added rows to N.",
    )
    grp.add_argument(
        "--max-removed",
        type=int,
        default=None,
        metavar="N",
        help="Cap the number of reported removed rows to N.",
    )
    grp.add_argument(
        "--max-modified",
        type=int,
        default=None,
        metavar="N",
        help="Cap the number of reported modified rows to N.",
    )


def opts_from_args(args: argparse.Namespace) -> LimitOptions:
    """Build a :class:`LimitOptions` from parsed CLI *args*."""
    return LimitOptions(
        max_changes=getattr(args, "max_changes", None),
        max_added=getattr(args, "max_added", None),
        max_removed=getattr(args, "max_removed", None),
        max_modified=getattr(args, "max_modified", None),
    )


def apply_limits(result: DiffResult, args: argparse.Namespace) -> DiffResult:
    """Convenience wrapper: build options from *args* and apply them."""
    opts = opts_from_args(args)
    limited = limit_diff(result, opts)
    dropped = len(result.changes) - len(limited.changes)
    if dropped:
        print(f"[limit] {limit_summary(result, opts)}")
    return limited
