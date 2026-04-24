"""CLI helpers for column aliasing (``--alias`` flag integration)."""

from __future__ import annotations

import argparse
from typing import List, Optional

from csvdiff.aliaser import AliasMap, alias_diff, build_alias_map
from csvdiff.differ import DiffResult


def add_alias_args(parser: argparse.ArgumentParser) -> None:
    """Register ``--alias`` argument on *parser*."""
    parser.add_argument(
        "--alias",
        metavar="ORIGINAL:DISPLAY",
        action="append",
        dest="aliases",
        default=[],
        help=(
            "Rename a column in the diff output.  "
            "May be specified multiple times, e.g. --alias first_name:'First Name'."
        ),
    )


def alias_map_from_args(args: argparse.Namespace) -> Optional[AliasMap]:
    """Return an AliasMap built from parsed CLI args, or *None* if none given."""
    pairs: List[str] = getattr(args, "aliases", []) or []
    if not pairs:
        return None
    try:
        return build_alias_map(pairs)
    except ValueError as exc:
        raise SystemExit(f"csvdiff: invalid --alias value — {exc}") from exc


def apply_aliases(
    result: DiffResult,
    args: argparse.Namespace,
) -> DiffResult:
    """Apply any ``--alias`` mappings from *args* to *result*.

    Returns *result* unchanged when no aliases are specified.
    """
    alias_map = alias_map_from_args(args)
    if alias_map is None:
        return result
    return alias_diff(result, alias_map)


def alias_summary(alias_map: Optional[AliasMap]) -> str:
    """Return a human-readable description of active aliases."""
    if alias_map is None or not alias_map.mapping:
        return "No column aliases active."
    lines = ["Active column aliases:"]
    for original, display in sorted(alias_map.mapping.items()):
        lines.append(f"  {original!r:30s} -> {display!r}")
    return "\n".join(lines)
