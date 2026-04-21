"""Tests for csvdiff.deduplicator."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.deduplicator import (
    find_duplicates,
    deduplicate,
    deduplicate_summary,
)


def _added(key: str) -> RowChange:
    return RowChange(key_value=key, change_type="added", old_row=None, new_row={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(key_value=key, change_type="removed", old_row={"id": key}, new_row=None)


def _modified(key: str) -> RowChange:
    return RowChange(
        key_value=key,
        change_type="modified",
        old_row={"id": key, "v": "a"},
        new_row={"id": key, "v": "b"},
    )


def _result(*changes) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged_count=0)


# --- find_duplicates ---

def test_find_duplicates_none():
    r = _result(_added("1"), _removed("2"))
    assert find_duplicates(r) == []


def test_find_duplicates_detects_duplicate():
    dup = _added("1")
    r = _result(_added("1"), dup)
    dupes = find_duplicates(r)
    assert len(dupes) == 1
    assert dupes[0] is dup


def test_find_duplicates_different_types_not_duplicate():
    r = _result(_added("1"), _removed("1"))
    assert find_duplicates(r) == []


# --- deduplicate (first strategy) ---

def test_deduplicate_no_dupes_unchanged():
    r = _result(_added("1"), _removed("2"))
    result = deduplicate(r)
    assert len(result.changes) == 2


def test_deduplicate_keeps_first():
    first = _added("1")
    second = _added("1")
    r = _result(first, second)
    result = deduplicate(r, strategy="first")
    assert len(result.changes) == 1
    assert result.changes[0] is first


def test_deduplicate_keeps_last():
    first = _added("1")
    second = _added("1")
    r = _result(first, second)
    result = deduplicate(r, strategy="last")
    assert len(result.changes) == 1
    assert result.changes[0] is second


def test_deduplicate_preserves_unchanged_count():
    r = DiffResult(changes=[_added("1"), _added("1")], unchanged_count=5)
    result = deduplicate(r)
    assert result.unchanged_count == 5


def test_deduplicate_invalid_strategy_raises():
    r = _result(_added("1"))
    with pytest.raises(ValueError, match="Unknown deduplication strategy"):
        deduplicate(r, strategy="random")  # type: ignore


# --- deduplicate_summary ---

def test_summary_no_duplicates():
    r = _result(_added("1"))
    msg = deduplicate_summary(r, r)
    assert "No duplicate" in msg


def test_summary_with_duplicates():
    original = _result(_added("1"), _added("1"), _removed("2"))
    deduped = deduplicate(original)
    msg = deduplicate_summary(original, deduped)
    assert "1 duplicate" in msg
    assert "2 unique" in msg
