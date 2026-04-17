"""Tests for csvdiff.formatter."""

import io
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.formatter import format_diff, format_summary


def make_result(added=None, removed=None, changed=None):
    r = DiffResult()
    r.added = added or {}
    r.removed = removed or {}
    r.changed = changed or {}
    return r


def test_no_changes_message():
    out = io.StringIO()
    format_diff(make_result(), use_color=False, out=out)
    assert "No differences found" in out.getvalue()


def test_added_row_shown():
    out = io.StringIO()
    result = make_result(added={"1": {"id": "1", "name": "Alice"}})
    format_diff(result, use_color=False, out=out)
    text = out.getvalue()
    assert "+ [1]" in text
    assert "Alice" in text


def test_removed_row_shown():
    out = io.StringIO()
    result = make_result(removed={"2": {"id": "2", "name": "Bob"}})
    format_diff(result, use_color=False, out=out)
    text = out.getvalue()
    assert "- [2]" in text
    assert "Bob" in text


def test_changed_row_shown():
    out = io.StringIO()
    change = RowChange(key="3", field_changes={"name": ("Old", "New")})
    result = make_result(changed={"3": change})
    format_diff(result, use_color=False, out=out)
    text = out.getvalue()
    assert "~ [3]" in text
    assert "'Old' -> 'New'" in text


def test_summary_counts():
    out = io.StringIO()
    change = RowChange(key="3", field_changes={"name": ("Old", "New")})
    result = make_result(
        added={"1": {}},
        removed={"2": {}},
        changed={"3": change},
    )
    format_summary(result, out=out)
    assert "1 added" in out.getvalue()
    assert "1 removed" in out.getvalue()
    assert "1 changed" in out.getvalue()


def test_summary_no_changes():
    out = io.StringIO()
    format_summary(make_result(), out=out)
    assert "0 added, 0 removed, 0 changed" in out.getvalue()
