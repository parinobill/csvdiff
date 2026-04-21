"""Tests for csvdiff.limiter."""

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.limiter import LimitOptions, limit_diff, limit_summary


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", old_row={}, new_row={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(key=key, change_type="removed", old_row={"id": key}, new_row={})


def _modified(key: str) -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        old_row={"id": key, "v": "1"},
        new_row={"id": key, "v": "2"},
    )


def _result(*changes) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged_count=0)


# ---------------------------------------------------------------------------
# limit_diff
# ---------------------------------------------------------------------------

def test_no_limits_returns_all_changes():
    result = _result(_added("1"), _removed("2"), _modified("3"))
    out = limit_diff(result, LimitOptions())
    assert len(out.changes) == 3


def test_max_changes_global_cap():
    result = _result(_added("1"), _added("2"), _added("3"))
    out = limit_diff(result, LimitOptions(max_changes=2))
    assert len(out.changes) == 2


def test_max_added_caps_only_added():
    result = _result(_added("1"), _added("2"), _removed("3"))
    out = limit_diff(result, LimitOptions(max_added=1))
    added = [c for c in out.changes if c.change_type == "added"]
    removed = [c for c in out.changes if c.change_type == "removed"]
    assert len(added) == 1
    assert len(removed) == 1


def test_max_removed_caps_only_removed():
    result = _result(_removed("1"), _removed("2"), _modified("3"))
    out = limit_diff(result, LimitOptions(max_removed=1))
    removed = [c for c in out.changes if c.change_type == "removed"]
    assert len(removed) == 1


def test_max_modified_caps_only_modified():
    result = _result(_modified("1"), _modified("2"), _added("3"))
    out = limit_diff(result, LimitOptions(max_modified=1))
    modified = [c for c in out.changes if c.change_type == "modified"]
    assert len(modified) == 1


def test_global_cap_applied_after_per_type_caps():
    result = _result(_added("1"), _added("2"), _removed("3"), _removed("4"))
    # per-type: 2 added, 2 removed -> 4 total; global cap -> 3
    out = limit_diff(result, LimitOptions(max_changes=3))
    assert len(out.changes) == 3


def test_unchanged_count_preserved():
    result = DiffResult(changes=[_added("1")], unchanged_count=99)
    out = limit_diff(result, LimitOptions(max_changes=1))
    assert out.unchanged_count == 99


def test_empty_result_returns_empty():
    result = _result()
    out = limit_diff(result, LimitOptions(max_changes=5))
    assert out.changes == []


# ---------------------------------------------------------------------------
# limit_summary
# ---------------------------------------------------------------------------

def test_summary_no_limit():
    result = _result(_added("1"), _removed("2"))
    msg = limit_summary(result, LimitOptions())
    assert "2" in msg
    assert "no limit" in msg


def test_summary_with_limit():
    result = _result(_added("1"), _added("2"), _added("3"))
    msg = limit_summary(result, LimitOptions(max_changes=2))
    assert "2 of 3" in msg
