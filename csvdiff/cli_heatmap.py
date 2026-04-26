"""CLI sub-command: heatmap — show which (row, field) cells changed most."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csvdiff.differ_heatmap import DiffHeatmap, HeatmapCell, build_heatmap
from csvdiff.differ import DiffResult


def add_heatmap_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "heatmap",
        help="Show a heatmap of which cells changed most across one or more diffs.",
    )
    p.add_argument("--top", type=int, default=20, metavar="N",
                   help="Show only the top N hottest cells (default: 20).")
    p.add_argument("--format", choices=["text", "json", "csv"], default="text",
                   help="Output format.")
    p.set_defaults(func=cmd_heatmap)


def _render_text(cells: List[HeatmapCell], hm: DiffHeatmap) -> str:
    if not cells:
        return "No changes found."
    lines = ["Heatmap (row_key : field  →  changes)", "-" * 40]
    for c in cells:
        lines.append(f"  {c.row_key:<20} {c.field_name:<20} {c.change_count:>5}")
    lines.append("")
    lines.append(hm.summary())
    hottest = hm.hottest_field()
    if hottest:
        lines.append(f"Hottest field overall: {hottest}")
    return "\n".join(lines)


def _render_json(cells: List[HeatmapCell]) -> str:
    data = [
        {"row_key": c.row_key, "field": c.field_name, "changes": c.change_count}
        for c in cells
    ]
    return json.dumps(data, indent=2)


def _render_csv(cells: List[HeatmapCell]) -> str:
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["row_key", "field", "changes"])
    writer.writeheader()
    for c in cells:
        writer.writerow({"row_key": c.row_key, "field": c.field_name, "changes": c.change_count})
    return buf.getvalue()


def cmd_heatmap(args: argparse.Namespace, result: DiffResult) -> int:
    hm = build_heatmap(result)
    cells = hm.top_cells(args.top)
    fmt = getattr(args, "format", "text")
    if fmt == "json":
        print(_render_json(cells))
    elif fmt == "csv":
        print(_render_csv(cells), end="")
    else:
        print(_render_text(cells, hm))
    return 0
