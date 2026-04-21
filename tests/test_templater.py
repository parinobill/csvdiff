"""Tests for csvdiff.templater."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.templater import list_builtin_formats, render_template


def _added(key: str, row: dict) -> RowChange:
    return RowChange(change_type="added", key=key, old_row=None, new_row=row)


def _removed(key: str, row: dict) -> RowChange:
    return RowChange(change_type="removed", key=key, old_row=row, new_row=None)


def _modified(key: str, old: dict, new: dict) -> RowChange:
    return RowChange(change_type="modified", key=key, old_row=old, new_row=new)


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged_count=0)


def test_render_text_no_changes():
    result = DiffResult(changes=[], unchanged_count=3)
    out = render_template(result, file_a="a.csv", file_b="b.csv", fmt="text")
    assert "a.csv" in out
    assert "b.csv" in out
    assert "Added rows   : 0" in out
    assert "(no changes)" in out


def test_render_text_with_added():
    result = _result(_added("1", {"id": "1", "name": "Alice"}))
    out = render_template(result, file_a="old.csv", file_b="new.csv", fmt="text")
    assert "Added rows   : 1" in out
    assert "Removed rows : 0" in out


def test_render_html_format():
    result = _result(_removed("2", {"id": "2", "name": "Bob"}))
    out = render_template(result, fmt="html")
    assert "<html>" in out
    assert "<td>Removed</td><td>1</td>" in out


def test_render_custom_template():
    tmpl = "added=$added removed=$removed"
    result = _result(
        _added("1", {"id": "1"}),
        _added("2", {"id": "2"}),
    )
    out = render_template(result, template_str=tmpl)
    assert out == "added=2 removed=0"


def test_render_modified_row_appears_in_change_lines():
    result = _result(_modified("3", {"id": "3", "v": "x"}, {"id": "3", "v": "y"}))
    out = render_template(result, fmt="text")
    assert "Modified rows: 1" in out
    # change_lines should contain the string repr of the change
    assert "3" in out


def test_unchanged_count_reflected():
    result = DiffResult(changes=[], unchanged_count=10)
    out = render_template(result, fmt="text")
    assert "Unchanged    : 10" in out
    assert "Total rows   : 10" in out


def test_list_builtin_formats():
    formats = list_builtin_formats()
    assert "text" in formats
    assert "html" in formats


def test_safe_substitute_ignores_unknown_placeholders():
    tmpl = "added=$added unknown=$unknown_var"
    result = DiffResult(changes=[], unchanged_count=0)
    # safe_substitute should not raise on unknown placeholder
    out = render_template(result, template_str=tmpl)
    assert "added=0" in out
    assert "$unknown_var" in out
