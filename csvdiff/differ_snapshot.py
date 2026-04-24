"""Snapshot diffing: compare a live CSV against a saved snapshot."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult
from csvdiff.pipeline import PipelineOptions, run_pipeline


@dataclass
class SnapshotMeta:
    label: str
    source_path: str
    key_column: str
    row_count: int

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "source_path": self.source_path,
            "key_column": self.key_column,
            "row_count": self.row_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SnapshotMeta":
        return cls(
            label=d["label"],
            source_path=d["source_path"],
            key_column=d["key_column"],
            row_count=int(d["row_count"]),
        )


@dataclass
class Snapshot:
    meta: SnapshotMeta
    rows: List[Dict[str, str]] = field(default_factory=list)

    def save(self, path: str) -> None:
        payload = {"meta": self.meta.to_dict(), "rows": self.rows}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    @classmethod
    def load(cls, path: str) -> "Snapshot":
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        return cls(
            meta=SnapshotMeta.from_dict(payload["meta"]),
            rows=payload["rows"],
        )


def capture_snapshot(
    csv_path: str,
    key_column: str,
    label: Optional[str] = None,
) -> Snapshot:
    """Read *csv_path* and return a Snapshot ready to be saved."""
    import csv

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    if rows and key_column not in rows[0]:
        raise KeyError(f"Key column '{key_column}' not found in {csv_path}")

    meta = SnapshotMeta(
        label=label or os.path.basename(csv_path),
        source_path=csv_path,
        key_column=key_column,
        row_count=len(rows),
    )
    return Snapshot(meta=meta, rows=rows)


def diff_snapshot(
    snapshot: Snapshot,
    current_csv: str,
    options: Optional[PipelineOptions] = None,
) -> DiffResult:
    """Diff *snapshot* rows against *current_csv* using the standard pipeline."""
    import csv
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    ) as tmp:
        if snapshot.rows:
            writer = csv.DictWriter(tmp, fieldnames=list(snapshot.rows[0].keys()))
            writer.writeheader()
            writer.writerows(snapshot.rows)
        tmp_path = tmp.name

    try:
        opts = options or PipelineOptions(key_column=snapshot.meta.key_column)
        if opts.key_column is None:
            opts = PipelineOptions(
                key_column=snapshot.meta.key_column,
                ignore_columns=opts.ignore_columns,
                include_columns=opts.include_columns,
            )
        return run_pipeline(tmp_path, current_csv, opts)
    finally:
        os.unlink(tmp_path)
