"""Integration tests for templater: verifies stats + change lines together."""

from __future__ import annotations

from csvdiff.differ import DiffResult, RowChange
from csvdiff.templater import render_template


def _rc(change_type, key, old=None, new=None):
    return RowChange(change_type=change_type, key=key, old_row=old, new_row=new)


def _result(changes, unchanged=0):
    return DiffResult(changes=changes, unchanged_count=unchanged)


def test_total_includes_unchanged():
    result = _result(
        [_rc("added", "1", new={"id": "1"})],
        unchanged=5,
    )
    out = render_template(result, fmt="text")
    assert "Total rows   : 6" in out
    assert "Unchanged    : 5" in out


def test_multiple_change_types_counted_correctly():
    changes = [
        _rc("added", "1", new={"id": "1"}),
        _rc("added", "2", new={"id": "2"}),
        _rc("removed", "3", old={"id": "3"}),
        _rc("modified", "4", old={"id": "4", "v": "a"}, new={"id": "4", "v": "b"}),
    ]
    result = _result(changes, unchanged=1)
    out = render_template(result, fmt="text")
    assert "Added rows   : 2" in out
    assert "Removed rows : 1" in out
    assert "Modified rows: 1" in out
    assert "Unchanged    : 1" in out
    assert "Total rows   : 5" in out


def test_html_contains_all_rows():
    changes = [
        _rc("added", "10", new={"id": "10"}),
    ]
    result = _result(changes, unchanged=2)
    out = render_template(result, fmt="html")
    assert "<td>Added</td><td>1</td>" in out
    assert "<td>Unchanged</td><td>2</td>" in out
    assert "<td>Total</td><td>3</td>" in out


def test_file_labels_appear_in_output():
    result = _result([])
    out = render_template(result, file_a="before.csv", file_b="after.csv", fmt="text")
    assert "before.csv" in out
    assert "after.csv" in out


def test_empty_diff_shows_no_changes_sentinel():
    result = _result([], unchanged=0)
    out = render_template(result, fmt="text")
    assert "(no changes)" in out
