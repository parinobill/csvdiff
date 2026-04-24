"""Tests for csvdiff.differ_snapshot."""
from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path

import pytest

from csvdiff.differ_snapshot import (
    Snapshot,
    SnapshotMeta,
    capture_snapshot,
    diff_snapshot,
)


def _write_csv(path: str, rows: list[dict]) -> None:
    if not rows:
        Path(path).write_text("")
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


# ---------------------------------------------------------------------------
# SnapshotMeta round-trip
# ---------------------------------------------------------------------------

def test_snapshot_meta_round_trip():
    meta = SnapshotMeta(label="v1", source_path="a.csv", key_column="id", row_count=5)
    assert SnapshotMeta.from_dict(meta.to_dict()) == meta


# ---------------------------------------------------------------------------
# capture_snapshot
# ---------------------------------------------------------------------------

def test_capture_snapshot_basic(tmp):
    csv_path = str(tmp / "data.csv")
    _write_csv(csv_path, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    snap = capture_snapshot(csv_path, key_column="id", label="test")
    assert snap.meta.row_count == 2
    assert snap.meta.label == "test"
    assert snap.meta.key_column == "id"
    assert len(snap.rows) == 2


def test_capture_snapshot_missing_file():
    with pytest.raises(FileNotFoundError):
        capture_snapshot("/nonexistent/path.csv", key_column="id")


def test_capture_snapshot_missing_key_column(tmp):
    csv_path = str(tmp / "data.csv")
    _write_csv(csv_path, [{"name": "Alice"}])
    with pytest.raises(KeyError, match="key_col"):
        capture_snapshot(csv_path, key_column="key_col")


# ---------------------------------------------------------------------------
# Snapshot.save / Snapshot.load
# ---------------------------------------------------------------------------

def test_snapshot_save_and_load(tmp):
    snap_path = str(tmp / "snap.json")
    meta = SnapshotMeta(label="v1", source_path="a.csv", key_column="id", row_count=1)
    snap = Snapshot(meta=meta, rows=[{"id": "1", "val": "x"}])
    snap.save(snap_path)

    loaded = Snapshot.load(snap_path)
    assert loaded.meta == meta
    assert loaded.rows == snap.rows


def test_snapshot_save_produces_valid_json(tmp):
    snap_path = str(tmp / "snap.json")
    meta = SnapshotMeta(label="l", source_path="b.csv", key_column="id", row_count=0)
    Snapshot(meta=meta, rows=[]).save(snap_path)
    with open(snap_path) as fh:
        payload = json.load(fh)
    assert "meta" in payload and "rows" in payload


# ---------------------------------------------------------------------------
# diff_snapshot
# ---------------------------------------------------------------------------

def test_diff_snapshot_detects_added_row(tmp):
    old_rows = [{"id": "1", "v": "a"}]
    new_rows = [{"id": "1", "v": "a"}, {"id": "2", "v": "b"}]
    csv_path = str(tmp / "data.csv")
    _write_csv(csv_path, old_rows)
    snap = capture_snapshot(csv_path, key_column="id")

    current_path = str(tmp / "current.csv")
    _write_csv(current_path, new_rows)
    result = diff_snapshot(snap, current_path)
    assert len(result.added) == 1
    assert result.added[0].key == "2"


def test_diff_snapshot_detects_removed_row(tmp):
    old_rows = [{"id": "1", "v": "a"}, {"id": "2", "v": "b"}]
    csv_path = str(tmp / "data.csv")
    _write_csv(csv_path, old_rows)
    snap = capture_snapshot(csv_path, key_column="id")

    current_path = str(tmp / "current.csv")
    _write_csv(current_path, [{"id": "1", "v": "a"}])
    result = diff_snapshot(snap, current_path)
    assert len(result.removed) == 1


def test_diff_snapshot_no_changes(tmp):
    rows = [{"id": "1", "v": "a"}]
    csv_path = str(tmp / "data.csv")
    _write_csv(csv_path, rows)
    snap = capture_snapshot(csv_path, key_column="id")

    current_path = str(tmp / "current.csv")
    _write_csv(current_path, rows)
    result = diff_snapshot(snap, current_path)
    assert not result.has_changes()
