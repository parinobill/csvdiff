"""Tests for csvdiff.baseline."""

import json
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.baseline import (
    save_baseline,
    load_baseline,
    diff_against_baseline,
    baseline_summary,
)


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", old_row=None, new_row={"id": key, "v": "1"})


def _removed(key: str) -> RowChange:
    return RowChange(key=key, change_type="removed", old_row={"id": key, "v": "0"}, new_row=None)


def _modified(key: str) -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        old_row={"id": key, "v": "0"},
        new_row={"id": key, "v": "1"},
    )


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(key_column="id", changes=list(changes))


# ---------------------------------------------------------------------------
# save / load roundtrip
# ---------------------------------------------------------------------------

def test_save_creates_file(tmp_path):
    path = tmp_path / "baseline.json"
    save_baseline(_result(_added("1")), path)
    assert path.exists()


def test_save_valid_json(tmp_path):
    path = tmp_path / "baseline.json"
    save_baseline(_result(_added("1"), _removed("2")), path)
    data = json.loads(path.read_text())
    assert data["key_column"] == "id"
    assert len(data["changes"]) == 2


def test_load_roundtrip(tmp_path):
    original = _result(_added("A"), _modified("B"), _removed("C"))
    path = tmp_path / "baseline.json"
    save_baseline(original, path)
    loaded = load_baseline(path)
    assert loaded.key_column == "id"
    assert len(loaded.changes) == 3
    keys = {c.key for c in loaded.changes}
    assert keys == {"A", "B", "C"}


def test_load_preserves_change_type(tmp_path):
    path = tmp_path / "b.json"
    save_baseline(_result(_modified("X")), path)
    loaded = load_baseline(path)
    assert loaded.changes[0].change_type == "modified"


# ---------------------------------------------------------------------------
# diff_against_baseline
# ---------------------------------------------------------------------------

def test_no_new_no_resolved():
    base = _result(_added("1"))
    current = _result(_added("1"))
    new, resolved = diff_against_baseline(current, base)
    assert new == []
    assert resolved == []


def test_detects_new_change():
    base = _result(_added("1"))
    current = _result(_added("1"), _removed("2"))
    new, resolved = diff_against_baseline(current, base)
    assert len(new) == 1
    assert new[0].key == "2"


def test_detects_resolved_change():
    base = _result(_added("1"), _modified("3"))
    current = _result(_added("1"))
    _, resolved = diff_against_baseline(current, base)
    assert len(resolved) == 1
    assert resolved[0].key == "3"


# ---------------------------------------------------------------------------
# baseline_summary
# ---------------------------------------------------------------------------

def test_summary_no_changes():
    msg = baseline_summary([], [])
    assert "No changes" in msg


def test_summary_new_and_resolved():
    msg = baseline_summary([_added("x")], [_removed("y")])
    assert "New changes" in msg
    assert "Resolved" in msg
