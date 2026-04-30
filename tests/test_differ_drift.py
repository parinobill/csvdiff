"""Tests for csvdiff.differ_drift."""
import pytest
from csvdiff.differ_drift import detect_drift, SchemaDrift


def test_no_drift_identical_columns():
    cols = ["id", "name", "age"]
    drift = detect_drift(cols, cols)
    assert not drift.has_drift
    assert drift.added_columns == []
    assert drift.removed_columns == []
    assert not drift.reordered


def test_detects_added_column():
    old = ["id", "name"]
    new = ["id", "name", "email"]
    drift = detect_drift(old, new)
    assert drift.has_drift
    assert drift.added_columns == ["email"]
    assert drift.removed_columns == []
    assert not drift.reordered


def test_detects_removed_column():
    old = ["id", "name", "age"]
    new = ["id", "name"]
    drift = detect_drift(old, new)
    assert drift.has_drift
    assert drift.removed_columns == ["age"]
    assert drift.added_columns == []


def test_detects_reordered_columns():
    old = ["id", "name", "age"]
    new = ["id", "age", "name"]
    drift = detect_drift(old, new)
    assert drift.has_drift
    assert drift.reordered
    assert drift.added_columns == []
    assert drift.removed_columns == []


def test_combined_add_remove_reorder():
    old = ["id", "name", "age"]
    new = ["id", "email", "age", "name"]
    drift = detect_drift(old, new)
    assert drift.has_drift
    assert "email" in drift.added_columns
    assert "name" not in drift.added_columns
    assert drift.removed_columns == []
    assert drift.reordered  # age/name swapped in common subset


def test_summary_no_drift():
    drift = detect_drift(["a", "b"], ["a", "b"])
    assert drift.summary() == "No schema drift detected."


def test_summary_added():
    drift = detect_drift(["a"], ["a", "b"])
    assert "Added columns" in drift.summary()
    assert "b" in drift.summary()


def test_summary_removed():
    drift = detect_drift(["a", "b"], ["a"])
    assert "Removed columns" in drift.summary()


def test_summary_reordered():
    drift = detect_drift(["a", "b"], ["b", "a"])
    assert "Column order changed" in drift.summary()


def test_as_dict_keys():
    drift = detect_drift(["a", "b"], ["b", "c"])
    d = drift.as_dict()
    assert set(d.keys()) == {"added_columns", "removed_columns", "reordered", "old_order", "new_order"}
    assert d["added_columns"] == ["c"]
    assert d["removed_columns"] == ["a"]


def test_old_and_new_order_preserved():
    old = ["x", "y", "z"]
    new = ["z", "y", "x"]
    drift = detect_drift(old, new)
    assert drift.old_order == old
    assert drift.new_order == new
