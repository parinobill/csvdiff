"""Tests for csvdiff.reporter module."""
import json
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.reporter import render_report


def _make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def test_no_changes_text():
    result = _make_result()
    assert render_report(result, fmt="text") == "No differences found."


def test_no_changes_json():
    result = _make_result()
    data = json.loads(render_report(result, fmt="json"))
    assert data["summary"] == {"added": 0, "removed": 0, "changed": 0}
    assert data["added"] == []
    assert data["removed"] == []
    assert data["changed"] == []


def test_added_row_text():
    change = RowChange(key="1", old_row=None, new_row={"id": "1", "name": "Alice"}, field_changes=[])
    result = _make_result(added=[change])
    report = render_report(result, fmt="text")
    assert "+ [1] row added" in report
    assert "Alice" in report


def test_removed_row_json():
    change = RowChange(key="2", old_row={"id": "2", "name": "Bob"}, new_row=None, field_changes=[])
    result = _make_result(removed=[change])
    data = json.loads(render_report(result, fmt="json"))
    assert data["removed"][0]["key"] == "2"
    assert data["removed"][0]["row"]["name"] == "Bob"
    assert data["summary"]["removed"] == 1


def test_changed_row_text():
    change = RowChange(
        key="3",
        old_row={"id": "3", "age": "30"},
        new_row={"id": "3", "age": "31"},
        field_changes=[("age", "30", "31")],
    )
    result = _make_result(changed=[change])
    report = render_report(result, fmt="text")
    assert "~ [3] age: '30' -> '31'" in report


def test_changed_row_json():
    change = RowChange(
        key="3",
        old_row={"id": "3", "age": "30"},
        new_row={"id": "3", "age": "31"},
        field_changes=[("age", "30", "31")],
    )
    result = _make_result(changed=[change])
    data = json.loads(render_report(result, fmt="json"))
    assert data["changed"][0]["fields"]["age"] == {"old": "30", "new": "31"}


def test_text_report_ends_with_summary():
    change = RowChange(key="1", old_row=None, new_row={"id": "1"}, field_changes=[])
    result = _make_result(added=[change])
    report = render_report(result, fmt="text")
    assert report.strip().splitlines()[-1] == result.summary()
