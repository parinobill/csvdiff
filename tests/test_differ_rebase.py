"""Tests for csvdiff.differ_rebase."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_rebase import (
    RebaseConflict,
    RebaseResult,
    rebase_patch,
    rebase_summary,
)


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", before={}, after={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(key=key, change_type="removed", before={"id": key}, after={})


def _modified(key: str, field: str = "name") -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        before={"id": key, field: "old"},
        after={"id": key, field: "new"},
    )


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_no_conflicts_keeps_all_original_changes():
    original = _result(_added("1"), _modified("2"))
    upstream = _result(_added("3"))
    result = rebase_patch(original, upstream)
    assert not result.has_conflicts
    keys = {ch.key for ch in result.rebased.changes}
    assert keys == {"1", "2", "3"}


def test_conflicting_key_produces_conflict():
    original = _result(_modified("A"))
    upstream = _result(_modified("A"))
    result = rebase_patch(original, upstream)
    assert result.has_conflicts
    assert len(result.conflicts) == 1
    assert result.conflicts[0].key == "A"


def test_conflicting_key_excluded_from_rebased():
    original = _result(_modified("A"), _added("B"))
    upstream = _result(_removed("A"))
    result = rebase_patch(original, upstream)
    rebased_keys = {ch.key for ch in result.rebased.changes}
    assert "A" not in rebased_keys
    assert "B" in rebased_keys


def test_upstream_only_changes_included():
    original = _result(_added("1"))
    upstream = _result(_added("99"))
    result = rebase_patch(original, upstream)
    keys = {ch.key for ch in result.rebased.changes}
    assert "99" in keys


def test_empty_original_returns_upstream():
    upstream = _result(_added("X"), _modified("Y"))
    result = rebase_patch(_result(), upstream)
    assert not result.has_conflicts
    assert len(result.rebased.changes) == 2


def test_empty_upstream_returns_original():
    original = _result(_added("A"), _removed("B"))
    result = rebase_patch(original, _result())
    assert not result.has_conflicts
    assert len(result.rebased.changes) == 2


def test_rebase_summary_no_conflicts():
    original = _result(_added("1"))
    upstream = _result(_added("2"))
    result = rebase_patch(original, upstream)
    summary = rebase_summary(result)
    assert "2 change" in summary
    assert "0 conflict" in summary


def test_rebase_summary_with_conflicts():
    original = _result(_modified("Z"))
    upstream = _result(_modified("Z"))
    result = rebase_patch(original, upstream)
    summary = rebase_summary(result)
    assert "1 conflict" in summary
    assert "Z" in summary


def test_conflict_str_contains_key():
    c = RebaseConflict(key="k1", reason="test", ours=None, theirs=None)
    assert "k1" in str(c)
    assert "test" in str(c)
