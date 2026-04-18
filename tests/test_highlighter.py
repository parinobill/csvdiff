"""Tests for csvdiff.highlighter."""
import pytest
from csvdiff.differ import RowChange
from csvdiff.highlighter import get_field_diffs, highlight_change, highlight_all_changes


def _modified(key, old, new):
    return RowChange(key=key, change_type="modified", old=old, new=new)


def _added(key, new):
    return RowChange(key=key, change_type="added", old=None, new=new)


def _removed(key, old):
    return RowChange(key=key, change_type="removed", old=old, new=None)


def test_get_field_diffs_detects_changes():
    c = _modified("1", {"a": "x", "b": "y"}, {"a": "x", "b": "z"})
    diffs = get_field_diffs(c)
    assert diffs == [("b", "y", "z")]


def test_get_field_diffs_no_changes():
    c = _modified("1", {"a": "x"}, {"a": "x"})
    assert get_field_diffs(c) == []


def test_get_field_diffs_added_row_returns_empty():
    c = _added("1", {"a": "x"})
    assert get_field_diffs(c) == []


def test_get_field_diffs_removed_row_returns_empty():
    c = _removed("1", {"a": "x"})
    assert get_field_diffs(c) == []


def test_get_field_diffs_multiple_fields():
    c = _modified("1", {"a": "1", "b": "2", "c": "3"}, {"a": "9", "b": "2", "c": "8"})
    diffs = get_field_diffs(c)
    fields = [d[0] for d in diffs]
    assert "a" in fields and "c" in fields and "b" not in fields


def test_highlight_change_no_color():
    c = _modified("42", {"name": "Alice"}, {"name": "Bob"})
    out = highlight_change(c, use_color=False)
    assert "42" in out
    assert "Alice" in out
    assert "Bob" in out
    assert "name" in out


def test_highlight_change_with_color():
    c = _modified("1", {"x": "old"}, {"x": "new"})
    out = highlight_change(c, use_color=True)
    assert "\033[31m" in out
    assert "\033[32m" in out


def test_highlight_change_empty_for_no_diff():
    c = _modified("1", {"a": "same"}, {"a": "same"})
    assert highlight_change(c) == ""


def test_highlight_all_changes_only_modified():
    changes = [
        _modified("1", {"v": "a"}, {"v": "b"}),
        _added("2", {"v": "c"}),
        _removed("3", {"v": "d"}),
    ]
    result = highlight_all_changes(changes, use_color=False)
    assert "1" in result
    assert "2" not in result
    assert "3" not in result
