"""CLI sub-command for deduplicating a diff result before output.

Usage (integrated into the main CLI):
    csvdiff file_a.csv file_b.csv --dedup [--dedup-strategy first|last]
"""

import argparse
from csvdiff.differ import DiffResult
from csvdiff.deduplicator import deduplicate, deduplicate_summary


def add_dedup_args(parser: argparse.ArgumentParser) -> None:
    """Register deduplication arguments onto an existing ArgumentParser."""
    group = parser.add_argument_group("deduplication")
    group.add_argument(
        "--dedup",
        action="store_true",
        default=False,
        help="Remove duplicate change entries before output.",
    )
    group.add_argument(
        "--dedup-strategy",
        choices=["first", "last"],
        default="first",
        dest="dedup_strategy",
        help="Which occurrence to keep when deduplicating (default: first).",
    )


def apply_dedup(result: DiffResult, args: argparse.Namespace) -> DiffResult:
    """Apply deduplication to *result* if requested via *args*.

    Args:
        result: The DiffResult produced by the diff pipeline.
        args:   Parsed CLI arguments (must have been processed by add_dedup_args).

    Returns:
        The original result unchanged, or a deduplicated copy.
    """
    if not getattr(args, "dedup", False):
        return result

    strategy = getattr(args, "dedup_strategy", "first")
    deduped = deduplicate(result, strategy=strategy)
    summary = deduplicate_summary(result, deduped)
    # Print to stderr so it doesn't pollute stdout output
    import sys
    print(f"[dedup] {summary}", file=sys.stderr)
    return deduped


def cmd_dedup(args: argparse.Namespace, result: DiffResult) -> DiffResult:
    """Entry point for the dedup command; wraps apply_dedup for CLI dispatch."""
    return apply_dedup(result, args)
