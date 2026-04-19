"""Tests for csvdiff.truncator."""

import pytest
from csvdiff.truncator import truncate_value, truncate_change, truncate_diff, DEFAULT_MAX_LEN
from csvdiff.differ import RowChange, DiffResult


def _modified(key, before, after):
    return RowChange(change_type="modified", key=key, before=before, after=after)


def _added(key, after):
    return RowChange(change_type="added", key=key, before=None, after=after)


def _removed(key, before):
    return RowChange(change_type="removed", key=key, before=before, after=None)


def test_truncate_value_short_string_unchanged():
    assert truncate_value("hello", max_len=20) == "hello"


def test_truncate_value_exact_length_unchanged():
    s = "a" * 20
    assert truncate_value(s, max_len=20) == s


def test_truncate_value_long_string_truncated():
    s = "a" * 80
    result = truncate_value(s, max_len=20)
    assert len(result) == 20
    assert result.endswith("...")


def test_truncate_value_default_max_len():
    s = "x" * 100
    result = truncate_value(s)
    assert len(result) == DEFAULT_MAX_LEN
    assert result.endswith("...")


def test_truncate_change_modified():
    long_val = "z" * 80
    change = _modified("1", {"name": long_val}, {"name": "short"})
    result = truncate_change(change, max_len=20)
    assert len(result.before["name"]) == 20
    assert result.after["name"] == "short"


def test_truncate_change_added_no_before():
    change = _added("2", {"desc": "x" * 70})
    result = truncate_change(change, max_len=30)
    assert result.before is None
    assert len(result.after["desc"]) == 30


def test_truncate_change_removed_no_after():
    change = _removed("3", {"note": "y" * 70})
    result = truncate_change(change, max_len=30)
    assert result.after is None
    assert len(result.before["note"]) == 30


def test_truncate_change_preserves_key_and_type():
    change = _modified("id-99", {"a": "hello"}, {"a": "world"})
    result = truncate_change(change, max_len=50)
    assert result.key == "id-99"
    assert result.change_type == "modified"


def test_truncate_diff_all_changes_truncated():
    changes = [
        _modified("1", {"v": "a" * 80}, {"v": "b" * 80}),
        _added("2", {"v": "c" * 80}),
    ]
    diff = DiffResult(changes=changes)
    result = truncate_diff(diff, max_len=20)
    assert all(len(c.after["v"]) == 20 for c in result.changes if c.after)


def test_truncate_diff_empty():
    diff = DiffResult(changes=[])
    result = truncate_diff(diff)
    assert result.changes == []
