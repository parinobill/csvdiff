"""Tests for csvdiff.differ module."""

import pytest
from csvdiff.differ import diff_csv, DiffResult, RowChange


OLD_ROWS = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob",   "age": "25"},
    {"id": "3", "name": "Carol", "age": "40"},
]

NEW_ROWS = [
    {"id": "1", "name": "Alice", "age": "31"},   # age changed
    {"id": "2", "name": "Bob",   "age": "25"},   # unchanged
    {"id": "4", "name": "Dave",  "age": "22"},   # added
    # id=3 removed
]


def test_detects_added_row():
    result = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    assert len(result.added) == 1
    assert result.added[0]["id"] == "4"


def test_detects_removed_row():
    result = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    assert len(result.removed) == 1
    assert result.removed[0]["id"] == "3"


def test_detects_changed_field():
    result = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    assert len(result.changed) == 1
    change = result.changed[0]
    assert change.key == "1"
    assert change.field == "age"
    assert change.old_value == "30"
    assert change.new_value == "31"


def test_unchanged_row_not_reported():
    result = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    changed_keys = {c.key for c in result.changed}
    assert "2" not in changed_keys


def test_no_differences():
    result = diff_csv(OLD_ROWS, OLD_ROWS, key_column="id")
    assert not result.has_changes
    assert result.summary() == "No differences found."


def test_has_changes_true():
    result = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    assert result.has_changes


def test_summary_contains_symbols():
    result = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    summary = result.summary()
    assert "+" in summary
    assert "-" in summary
    assert "~" in summary


def test_empty_inputs():
    result = diff_csv([], [], key_column="id")
    assert not result.has_changes


def test_all_rows_added():
    result = diff_csv([], NEW_ROWS, key_column="id")
    assert len(result.added) == len(NEW_ROWS)
    assert not result.removed
    assert not result.changed
