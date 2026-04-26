"""CLI sub-command: cluster — group diff changes by key prefix."""
from __future__ import annotations

import argparse
import sys

from csvdiff.differ_cluster import cluster_diff, cluster_summary
from csvdiff.parser import read_csv
from csvdiff.differ import DiffResult


def add_cluster_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "cluster",
        help="Group diff changes into clusters by key-value prefix.",
    )
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="New CSV file")
    p.add_argument("--key", required=True, help="Key column name")
    p.add_argument(
        "--prefix-len",
        type=int,
        default=3,
        dest="prefix_len",
        help="Number of leading characters used to form cluster label (default: 3)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format",
    )
    p.set_defaults(func=cmd_cluster)


def cmd_cluster(args: argparse.Namespace) -> int:
    try:
        from csvdiff.differ import compute_diff  # type: ignore[attr-defined]
    except ImportError:
        # Fallback: build a minimal diff result from parser
        from csvdiff.pipeline import run_pipeline, PipelineOptions
        opts = PipelineOptions(key_column=args.key)
        result = run_pipeline(args.old, args.new, opts)
    else:
        result = compute_diff(
            read_csv(args.old, args.key),
            read_csv(args.new, args.key),
            key_column=args.key,
        )

    cr = cluster_diff(result, key_column=args.key, prefix_len=args.prefix_len)

    if args.fmt == "json":
        import json
        out = {
            "clusters": {
                label: {
                    "count": len(c),
                    "change_types": c.change_types(),
                }
                for label, c in cr.clusters.items()
            },
            "unclustered": len(cr.unclustered),
        }
        print(json.dumps(out, indent=2))
    else:
        print(cluster_summary(cr))

    return 0 if cr.total_clustered() == 0 and not cr.unclustered else 1
