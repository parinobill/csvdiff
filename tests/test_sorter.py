"""Tests for csvdiff.sorter."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.sorter import sort_changes, get_sort_key_values


def _make_result():
    return DiffResult(
        added=[RowChange(key="charlie", change_type="added", fields={})],
        removed=[RowChange(key="alice", change_type="removed", fields={})],
        changed=[RowChange(key="bob", change_type="changed", fields={"age": ("30", "31")})],
    )


def test_sort_by_key_ascending():
    result = _make_result()
    sorted_result = sort_changes(result, by="key")
    keys = get_sort_key_values(sorted_result)
    assert keys == sorted(keys)


def test_sort_by_key_descending():
    result = _make_result()
    sorted_result = sort_changes(result, by="key", reverse=True)
    keys = get_sort_key_values(sorted_result)
    assert keys == sorted(keys, reverse=True)


def test_sort_by_change_type():
    result = _make_result()
    sorted_result = sort_changes(result, by="change_type")
    types = [c.change_type for c in sorted_result.changes]
    assert types == sorted(types)


def test_invalid_sort_field_raises():
    result = _make_result()
    with pytest.raises(ValueError, match="Cannot sort by"):
        sort_changes(result, by="nonexistent_field")


def test_sort_preserves_all_changes():
    result = _make_result()
    sorted_result = sort_changes(result, by="key")
    assert len(sorted_result.changes) == len(result.changes)


def test_get_sort_key_values_returns_all_keys():
    result = _make_result()
    keys = get_sort_key_values(result)
    assert set(keys) == {"alice", "bob", "charlie"}


def test_sort_empty_result():
    empty = DiffResult(added=[], removed=[], changed=[])
    sorted_result = sort_changes(empty, by="key")
    assert sorted_result.changes == []
