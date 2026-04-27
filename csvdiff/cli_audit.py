"""CLI subcommands for audit-trail features."""
from __future__ import annotations

import argparse
import json
import sys

from csvdiff.differ_audit import AuditMeta, AuditedResult, audit_result
from csvdiff.pipeline import PipelineOptions, run_pipeline


def add_audit_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("audit", help="Diff two CSV files and emit an audited report")
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="Updated CSV file")
    p.add_argument("--key", required=True, help="Key column name")
    p.add_argument("--label", default=None, help="Human-readable label for this run")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.set_defaults(func=cmd_audit)


def cmd_audit(args: argparse.Namespace) -> int:
    opts = PipelineOptions(key_column=args.key)
    try:
        result = run_pipeline(args.old, args.new, opts)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    audited = audit_result(result, label=args.label)

    if args.fmt == "json":
        _render_json(audited)
    else:
        _render_text(audited)

    return 1 if result.has_changes() else 0


def _render_text(audited: AuditedResult) -> None:
    print(audited.summary())


def _render_json(audited: AuditedResult) -> None:
    from csvdiff.differ_patch import build_patch

    patch_dict = build_patch(audited.result).to_dict()
    out = {"audit": audited.meta.to_dict(), "patch": patch_dict}
    print(json.dumps(out, indent=2))
