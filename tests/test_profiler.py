"""Tests for csvdiff.profiler."""

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.profiler import ColumnProfile, DiffProfile, profile_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key, row):
    return RowChange(key=key, old=None, new=row)


def _removed(key, row):
    return RowChange(key=key, old=row, new=None)


def _modified(key, old, new):
    return RowChange(key=key, old=old, new=new)


def _result(*changes):
    return DiffResult(changes=list(changes))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_profile_empty_result():
    prof = profile_diff(_result())
    assert prof.total_rows_affected == 0
    assert prof.added == 0
    assert prof.removed == 0
    assert prof.modified == 0
    assert prof.column_profiles == {}


def test_profile_counts_added():
    prof = profile_diff(_result(_added("1", {"id": "1", "name": "Alice"})))
    assert prof.added == 1
    assert prof.removed == 0
    assert prof.modified == 0


def test_profile_counts_removed():
    prof = profile_diff(_result(_removed("2", {"id": "2", "name": "Bob"})))
    assert prof.removed == 1
    assert prof.added == 0


def test_profile_counts_modified():
    prof = profile_diff(
        _result(_modified("3", {"id": "3", "val": "x"}, {"id": "3", "val": "y"}))
    )
    assert prof.modified == 1


def test_column_profile_tracks_changed_column():
    prof = profile_diff(
        _result(_modified("3", {"id": "3", "val": "x"}, {"id": "3", "val": "y"}))
    )
    assert "val" in prof.column_profiles
    cp = prof.column_profiles["val"]
    assert cp.change_count == 1
    assert "3" in cp.affected_keys


def test_unchanged_column_not_in_profile():
    prof = profile_diff(
        _result(_modified("3", {"id": "3", "val": "x"}, {"id": "3", "val": "y"}))
    )
    assert "id" not in prof.column_profiles


def test_multiple_rows_same_column():
    changes = [
        _modified("1", {"id": "1", "score": "10"}, {"id": "1", "score": "20"}),
        _modified("2", {"id": "2", "score": "30"}, {"id": "2", "score": "40"}),
    ]
    prof = profile_diff(_result(*changes))
    assert prof.column_profiles["score"].change_count == 2


def test_most_changed_columns_ordering():
    changes = [
        _modified("1", {"a": "1", "b": "1"}, {"a": "2", "b": "2"}),
        _modified("2", {"a": "3", "b": "3"}, {"a": "4", "b": "3"}),
    ]
    prof = profile_diff(_result(*changes))
    top = prof.most_changed_columns(top_n=2)
    assert top[0].column == "a"
    assert top[0].change_count == 2


def test_column_profile_summary_string():
    cp = ColumnProfile(column="price", change_count=3, affected_keys=["1", "2", "3"])
    assert "price" in cp.summary
    assert "3" in cp.summary
