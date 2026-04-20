"""Tests for csvdiff.merger."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.merger import merge_results, merge_summary


COLS = ["id", "name", "score"]


def _added(key: str, row: dict) -> RowChange:
    return RowChange(key=key, change_type="added", before=None, after=row)


def _removed(key: str, row: dict) -> RowChange:
    return RowChange(key=key, change_type="removed", before=row, after=None)


def _modified(key: str, before: dict, after: dict) -> RowChange:
    return RowChange(key=key, change_type="modified", before=before, after=after)


def _result(changes, columns=None) -> DiffResult:
    return DiffResult(changes=changes, columns=columns or COLS)


def test_merge_empty_results():
    r = merge_results(_result([]), _result([]))
    assert r.changes == []


def test_overlay_adds_new_changes():
    base = _result([_added("1", {"id": "1", "name": "Alice", "score": "90"})])
    overlay = _result([_added("2", {"id": "2", "name": "Bob", "score": "80"})])
    merged = merge_results(base, overlay)
    keys = {c.key for c in merged.changes}
    assert keys == {"1", "2"}


def test_overlay_wins_on_conflict_by_default():
    before = {"id": "1", "name": "Alice", "score": "70"}
    after_base = {"id": "1", "name": "Alice", "score": "80"}
    after_overlay = {"id": "1", "name": "Alice", "score": "95"}
    base = _result([_modified("1", before, after_base)])
    overlay = _result([_modified("1", before, after_overlay)])
    merged = merge_results(base, overlay)
    assert len(merged.changes) == 1
    assert merged.changes[0].after["score"] == "95"


def test_base_wins_when_prefer_base():
    before = {"id": "1", "name": "Alice", "score": "70"}
    after_base = {"id": "1", "name": "Alice", "score": "80"}
    after_overlay = {"id": "1", "name": "Alice", "score": "95"}
    base = _result([_modified("1", before, after_base)])
    overlay = _result([_modified("1", before, after_overlay)])
    merged = merge_results(base, overlay, prefer="base")
    assert merged.changes[0].after["score"] == "80"


def test_invalid_prefer_raises():
    with pytest.raises(ValueError, match="prefer must be"):
        merge_results(_result([]), _result([]), prefer="neither")


def test_columns_extended_from_overlay():
    base = _result([], columns=["id", "name"])
    overlay = _result([], columns=["id", "name", "email"])
    merged = merge_results(base, overlay)
    assert merged.columns == ["id", "name", "email"]


def test_columns_not_duplicated():
    base = _result([], columns=["id", "name"])
    overlay = _result([], columns=["id", "name"])
    merged = merge_results(base, overlay)
    assert merged.columns == ["id", "name"]


def test_merge_summary_counts():
    changes = [
        _added("1", {"id": "1"}),
        _added("2", {"id": "2"}),
        _removed("3", {"id": "3"}),
        _modified("4", {"id": "4", "v": "a"}, {"id": "4", "v": "b"}),
    ]
    result = _result(changes)
    summary = merge_summary(result)
    assert summary == {"added": 2, "removed": 1, "modified": 1}


def test_merge_summary_empty():
    summary = merge_summary(_result([]))
    assert summary == {"added": 0, "removed": 0, "modified": 0}
