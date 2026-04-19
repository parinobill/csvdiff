"""Tests for csvdiff.grouper."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.grouper import group_by_change_type, group_by_field_value, group_summary


def _make_result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def _added(key, **after):
    return RowChange(key=key, change_type="added", before=None, after={"id": key, **after})


def _removed(key, **before):
    return RowChange(key=key, change_type="removed", before={"id": key, **before}, after=None)


def _modified(key, before, after):
    return RowChange(key=key, change_type="modified", before={"id": key, **before}, after={"id": key, **after})


def test_group_by_change_type_empty():
    result = _make_result()
    groups = group_by_change_type(result)
    assert groups == {}


def test_group_by_change_type_single_added():
    r = _make_result(_added("1", name="Alice"))
    groups = group_by_change_type(r)
    assert list(groups.keys()) == ["added"]
    assert len(groups["added"]) == 1


def test_group_by_change_type_mixed():
    r = _make_result(
        _added("1", name="Alice"),
        _removed("2", name="Bob"),
        _modified("3", {"name": "Carol"}, {"name": "Caroline"}),
        _added("4", name="Dave"),
    )
    groups = group_by_change_type(r)
    assert len(groups["added"]) == 2
    assert len(groups["removed"]) == 1
    assert len(groups["modified"]) == 1


def test_group_by_field_value_uses_after_for_added():
    r = _make_result(_added("1", dept="eng"), _added("2", dept="hr"))
    groups = group_by_field_value(r, "dept")
    assert set(groups.keys()) == {"eng", "hr"}


def test_group_by_field_value_uses_before_for_removed():
    r = _make_result(_removed("1", dept="eng"))
    groups = group_by_field_value(r, "dept")
    assert "eng" in groups


def test_group_by_field_value_missing_field_uses_empty_string():
    r = _make_result(_added("1", name="X"))  # no 'dept'
    groups = group_by_field_value(r, "dept")
    assert "" in groups


def test_group_summary_counts():
    r = _make_result(
        _added("1", dept="eng"),
        _added("2", dept="eng"),
        _removed("3", dept="hr"),
    )
    groups = group_by_field_value(r, "dept")
    summary = group_summary(groups)
    assert summary["eng"] == 2
    assert summary["hr"] == 1
