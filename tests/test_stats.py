"""Tests for csvdiff.stats module."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.stats import compute_stats, DiffStats


def _make_change(change_type: str, key: str = "1") -> RowChange:
    before = {"id": key, "name": "old"} if change_type != "added" else None
    after = {"id": key, "name": "new"} if change_type != "removed" else None
    fields = {"name": ("old", "new")} if change_type == "modified" else {}
    return RowChange(key=key, change_type=change_type, before=before, after=after, field_diffs=fields)


def _make_result(*change_types) -> DiffResult:
    changes = [_make_change(ct, str(i)) for i, ct in enumerate(change_types)]
    return DiffResult(changes=changes)


def test_no_changes():
    result = _make_result()
    stats = compute_stats(result, total_rows=5)
    assert stats.added == 0
    assert stats.removed == 0
    assert stats.modified == 0
    assert stats.unchanged == 5
    assert stats.changed == 0


def test_counts_added():
    result = _make_result("added", "added")
    stats = compute_stats(result, total_rows=5)
    assert stats.added == 2
    assert stats.unchanged == 3


def test_counts_removed():
    result = _make_result("removed")
    stats = compute_stats(result, total_rows=4)
    assert stats.removed == 1
    assert stats.unchanged == 3


def test_counts_modified():
    result = _make_result("modified", "modified", "modified")
    stats = compute_stats(result, total_rows=10)
    assert stats.modified == 3
    assert stats.unchanged == 7


def test_mixed_changes():
    result = _make_result("added", "removed", "modified")
    stats = compute_stats(result, total_rows=6)
    assert stats.added == 1
    assert stats.removed == 1
    assert stats.modified == 1
    assert stats.changed == 3
    assert stats.unchanged == 3


def test_as_dict_keys():
    result = _make_result("added")
    stats = compute_stats(result, total_rows=3)
    d = stats.as_dict()
    assert set(d.keys()) == {"added", "removed", "modified", "unchanged", "total_rows", "changed"}


def test_str_representation():
    stats = DiffStats(added=1, removed=2, modified=3, unchanged=4, total_rows=10)
    s = str(stats)
    assert "Added: 1" in s
    assert "Removed: 2" in s
    assert "Modified: 3" in s


def test_unchanged_never_negative():
    result = _make_result("added", "added", "added")
    stats = compute_stats(result, total_rows=1)
    assert stats.unchanged == 0
