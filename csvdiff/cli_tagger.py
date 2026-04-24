"""CLI integration for the tagger feature."""

from __future__ import annotations

import argparse
import sys
from typing import List

from csvdiff.tagger import TagRule, apply_tags, group_by_tag, tag_summary
from csvdiff.differ import DiffResult


def add_tagger_args(parser: argparse.ArgumentParser) -> None:
    """Register tagger sub-arguments onto an existing parser or sub-command."""
    parser.add_argument(
        "--tag",
        dest="tag_rules",
        metavar="TAG:TYPE[:FIELD[:VALUE]]",
        action="append",
        default=[],
        help=(
            "Define a tag rule. Format: label:change_type[:field_name[:value_substr]]. "
            "change_type may be 'added', 'removed', 'modified', or '*' for any."
        ),
    )
    parser.add_argument(
        "--tag-group",
        action="store_true",
        default=False,
        help="Print changes grouped by tag instead of a flat summary.",
    )


def _parse_tag_rules(raw_rules: List[str]) -> List[TagRule]:
    rules: List[TagRule] = []
    for raw in raw_rules:
        parts = raw.split(":", 3)
        if len(parts) < 2:
            print(f"[tagger] Skipping invalid rule (need at least TAG:TYPE): {raw!r}", file=sys.stderr)
            continue
        tag = parts[0]
        change_type: str | None = parts[1] if parts[1] != "*" else None
        field_name: str | None = parts[2] if len(parts) > 2 else None
        field_value: str | None = parts[3] if len(parts) > 3 else None
        rules.append(TagRule(tag=tag, change_type=change_type, field_name=field_name, field_value=field_value))
    return rules


def cmd_tag(result: DiffResult, args: argparse.Namespace) -> int:
    """Run the tagger command against a pre-computed DiffResult.

    Returns an exit code (0 = no changes, 1 = changes found).
    """
    rules = _parse_tag_rules(getattr(args, "tag_rules", []))
    tagged = apply_tags(result, rules)

    if getattr(args, "tag_group", False):
        groups = group_by_tag(tagged)
        for tag, items in sorted(groups.items()):
            label = tag if tag else "(untagged)"
            print(f"\n[{label}] ({len(items)} change(s))")
            for tc in items:
                print(f"  {tc}")
    else:
        print(tag_summary(tagged))

    return 1 if result.has_changes() else 0
