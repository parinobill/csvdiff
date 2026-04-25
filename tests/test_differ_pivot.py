"""Tests for csvdiff.differ_pivot."""
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_pivot import FieldPivot, pivot_diff, top_changed_fields


def _added(key: str, row: dict) -> RowChange:
    return RowChange(key=key, change_type="added", old_row={}, new_row=row, changed_fields=[])


def _removed(key: str, row: dict) -> RowChange:
    return RowChange(key=key, change_type="removed", old_row=row, new_row={}, changed_fields=[])


def _modified(key: str, old: dict, new: dict, fields: list) -> RowChange:
    return RowChange(key=key, change_type="modified", old_row=old, new_row=new, changed_fields=fields)


def _result(**kwargs) -> DiffResult:
    return DiffResult(
        added=kwargs.get("added", []),
        removed=kwargs.get("removed", []),
        modified=kwargs.get("modified", []),
        unchanged=kwargs.get("unchanged", []),
    )


def test_pivot_empty_result():
    result = _result()
    assert pivot_diff(result) == {}


def test_pivot_added_row_creates_entries():
    result = _result(added=[_added("1", {"name": "Alice", "age": "30"})])
    pivots = pivot_diff(result)
    assert "name" in pivots
    assert "age" in pivots
    assert pivots["name"].added_values == ["Alice"]
    assert pivots["age"].added_values == ["30"]


def test_pivot_removed_row_populates_removed_values():
    result = _result(removed=[_removed("2", {"name": "Bob", "score": "99"})])
    pivots = pivot_diff(result)
    assert pivots["name"].removed_values == ["Bob"]
    assert pivots["score"].removed_values == ["99"]


def test_pivot_modified_row_populates_old_and_new():
    old = {"name": "Carol", "score": "80"}
    new = {"name": "Carol", "score": "95"}
    result = _result(modified=[_modified("3", old, new, ["score"])])
    pivots = pivot_diff(result)
    assert "score" in pivots
    assert pivots["score"].old_values == ["80"]
    assert pivots["score"].new_values == ["95"]
    assert "name" not in pivots


def test_pivot_total_touches_counts_correctly():
    result = _result(
        added=[_added("1", {"x": "1"})],
        removed=[_removed("2", {"x": "2"})],
        modified=[_modified("3", {"x": "3"}, {"x": "4"}, ["x"])],
    )
    pivots = pivot_diff(result)
    assert pivots["x"].total_touches == 3


def test_field_pivot_summary_no_changes():
    p = FieldPivot(field_name="col")
    assert p.summary() == "col: no changes"


def test_field_pivot_summary_mixed():
    p = FieldPivot(field_name="col", added_values=["a"], old_values=["b", "c"])
    s = p.summary()
    assert "+1 added" in s
    assert "~2 modified" in s


def test_top_changed_fields_order():
    result = _result(
        added=[_added("1", {"a": "1", "b": "2"})],
        modified=[_modified("2", {"a": "x"}, {"a": "y"}, ["a"]),
                  _modified("3", {"a": "p"}, {"a": "q"}, ["a"])],
    )
    ranked = top_changed_fields(result)
    assert ranked[0].field_name == "a"


def test_top_changed_fields_cap():
    result = _result(added=[_added("1", {"x": "1", "y": "2", "z": "3"})])
    ranked = top_changed_fields(result, n=2)
    assert len(ranked) == 2
