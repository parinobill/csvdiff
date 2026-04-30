"""Tests for csvdiff.differ_variance."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_variance import FieldVariance, VarianceResult, compute_variance


def _modified(key: str, old: dict, new: dict) -> RowChange:
    return RowChange(change_type="modified", key=key, old_row=old, new_row=new)


def _added(key: str, row: dict) -> RowChange:
    return RowChange(change_type="added", key=key, old_row=None, new_row=row)


def _removed(key: str, row: dict) -> RowChange:
    return RowChange(change_type="removed", key=key, old_row=row, new_row=None)


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_empty_result_returns_empty_variance():
    vr = compute_variance(_result())
    assert vr.fields == {}


def test_added_and_removed_rows_ignored():
    r = _result(
        _added("1", {"id": "1", "val": "10"}),
        _removed("2", {"id": "2", "val": "20"}),
    )
    vr = compute_variance(r)
    assert vr.fields == {}


def test_single_modified_row_counts_changed_field():
    r = _result(_modified("1", {"id": "1", "price": "10"}, {"id": "1", "price": "20"}))
    vr = compute_variance(r)
    assert "price" in vr.fields
    assert vr.fields["price"].change_count == 1


def test_unchanged_field_not_counted():
    r = _result(_modified("1", {"id": "1", "name": "Alice"}, {"id": "1", "name": "Alice"}))
    vr = compute_variance(r)
    assert "name" not in vr.fields


def test_numeric_delta_computed():
    r = _result(_modified("1", {"id": "1", "score": "100"}, {"id": "1", "score": "150"}))
    vr = compute_variance(r)
    fv = vr.fields["score"]
    assert fv.mean_delta == pytest.approx(50.0)
    assert fv.max_delta == pytest.approx(50.0)


def test_non_numeric_field_has_no_delta():
    r = _result(_modified("1", {"id": "1", "status": "open"}, {"id": "1", "status": "closed"}))
    vr = compute_variance(r)
    fv = vr.fields["status"]
    assert fv.mean_delta is None
    assert fv.max_delta is None


def test_multiple_rows_accumulate_change_count():
    r = _result(
        _modified("1", {"id": "1", "qty": "1"}, {"id": "1", "qty": "2"}),
        _modified("2", {"id": "2", "qty": "3"}, {"id": "2", "qty": "5"}),
    )
    vr = compute_variance(r)
    assert vr.fields["qty"].change_count == 2


def test_top_returns_sorted_by_change_count():
    r = _result(
        _modified("1", {"id": "1", "a": "1", "b": "x"}, {"id": "1", "a": "2", "b": "y"}),
        _modified("2", {"id": "2", "a": "3"}, {"id": "2", "a": "4"}),
    )
    vr = compute_variance(r)
    top = vr.top(5)
    assert top[0].field_name == "a"
    assert top[0].change_count == 2


def test_summary_no_changes():
    vr = VarianceResult()
    assert vr.summary() == "No field variance detected."


def test_summary_with_changes():
    vr = VarianceResult(fields={"price": FieldVariance("price", change_count=3)})
    s = vr.summary()
    assert "price" in s
    assert "3 change" in s


def test_field_variance_summary_no_numeric():
    fv = FieldVariance("label", change_count=2)
    s = fv.summary()
    assert "label" in s
    assert "mean_delta" not in s
