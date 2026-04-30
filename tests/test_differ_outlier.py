"""Tests for csvdiff.differ_outlier."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_outlier import OutlierResult, detect_outliers


def _modified(key: str, fields_changed: dict) -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        old_row={},
        new_row={},
        fields_changed=fields_changed,
    )


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", old_row={}, new_row={}, fields_changed={})


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_empty_result_returns_no_outliers():
    r = detect_outliers(_result())
    assert r.outliers == []
    assert r.field_stats == {}


def test_added_rows_ignored():
    r = detect_outliers(_result(_added("r1")))
    assert r.outliers == []


def test_non_numeric_fields_ignored():
    ch = _modified("r1", {"name": ("Alice", "Bob")})
    r = detect_outliers(_result(ch))
    assert r.outliers == []


def test_single_modified_no_outlier_due_to_zero_std():
    ch = _modified("r1", {"price": ("10", "20")})
    r = detect_outliers(_result(ch))
    # std == 0 -> z == 0, below threshold
    assert r.outliers == []
    assert "price" in r.field_stats


def test_detects_outlier_with_high_z_score():
    # deltas: 1, 1, 1, 1, 100  — last is a clear outlier
    changes = [
        _modified(f"r{i}", {"val": (str(i), str(i + 1))})
        for i in range(4)
    ]
    changes.append(_modified("r99", {"val": ("0", "100")}))
    r = detect_outliers(_result(*changes), z_threshold=2.0)
    assert len(r.outliers) == 1
    assert r.outliers[0].change.key == "r99"
    assert r.outliers[0].field_name == "val"
    assert r.outliers[0].delta == pytest.approx(100.0)


def test_outlier_str_representation():
    changes = [
        _modified(f"r{i}", {"score": ("0", "1")}) for i in range(4)
    ]
    changes.append(_modified("outlier", {"score": ("0", "50")}))
    r = detect_outliers(_result(*changes), z_threshold=1.5)
    assert any("outlier" in str(o) for o in r.outliers)


def test_summary_no_outliers():
    r = OutlierResult()
    assert r.summary() == "No numeric outliers detected."


def test_summary_with_outliers():
    changes = [
        _modified(f"r{i}", {"x": ("0", "1")}) for i in range(4)
    ]
    changes.append(_modified("big", {"x": ("0", "99")}))
    r = detect_outliers(_result(*changes), z_threshold=1.5)
    summary = r.summary()
    assert "outlier" in summary.lower()
    assert "big" in summary


def test_field_stats_populated():
    changes = [
        _modified(f"r{i}", {"revenue": ("100", str(100 + i))}) for i in range(5)
    ]
    r = detect_outliers(_result(*changes))
    assert "revenue" in r.field_stats
    stats = r.field_stats["revenue"]
    assert "mean" in stats
    assert "std" in stats
    assert stats["n"] == 5


def test_multiple_fields_tracked_independently():
    changes = [
        _modified(f"r{i}", {"a": ("0", "1"), "b": ("10", "11")}) for i in range(4)
    ]
    changes.append(_modified("big_a", {"a": ("0", "100"), "b": ("10", "11")}))
    r = detect_outliers(_result(*changes), z_threshold=1.5)
    outlier_fields = {o.field_name for o in r.outliers}
    assert "a" in outlier_fields
    assert "b" not in outlier_fields
