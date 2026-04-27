"""Tests for csvdiff.differ_threshold."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_threshold import (
    ThresholdOptions,
    ThresholdResult,
    apply_threshold,
    _changed_field_count,
)


def _added(key: str) -> RowChange:
    return RowChange(change_type="added", key=key, old_row=None, new_row={"id": key, "v": "1"})


def _removed(key: str) -> RowChange:
    return RowChange(change_type="removed", key=key, old_row={"id": key, "v": "1"}, new_row=None)


def _modified(key: str, n_fields: int = 1) -> RowChange:
    old = {"id": key, **{f"f{i}": "old" for i in range(n_fields)}}
    new = {"id": key, **{f"f{i}": "new" for i in range(n_fields)}}
    return RowChange(change_type="modified", key=key, old_row=old, new_row=new)


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


# --- _changed_field_count ---

def test_changed_field_count_modified():
    assert _changed_field_count(_modified("k", 3)) == 3


def test_changed_field_count_added_returns_zero():
    assert _changed_field_count(_added("k")) == 0


def test_changed_field_count_removed_returns_zero():
    assert _changed_field_count(_removed("k")) == 0


# --- apply_threshold: min_changed_fields ---

def test_min_changed_fields_keeps_sufficient():
    opts = ThresholdOptions(min_changed_fields=2)
    r = apply_threshold(_result(_modified("k", 3)), opts)
    assert not r.suppressed
    assert len(r.kept) == 1
    assert len(r.dropped) == 0


def test_min_changed_fields_drops_insufficient():
    opts = ThresholdOptions(min_changed_fields=2)
    r = apply_threshold(_result(_modified("k", 1)), opts)
    assert not r.suppressed
    assert len(r.kept) == 0
    assert len(r.dropped) == 1


def test_added_and_removed_always_kept():
    opts = ThresholdOptions(min_changed_fields=99)
    r = apply_threshold(_result(_added("a"), _removed("b")), opts)
    assert len(r.kept) == 2
    assert len(r.dropped) == 0


# --- apply_threshold: suppression ---

def test_require_min_rows_suppresses_when_below():
    opts = ThresholdOptions(require_min_rows=10)
    r = apply_threshold(_result(_added("a")), opts)
    assert r.suppressed


def test_require_min_rows_passes_when_met():
    changes = [_added(str(i)) for i in range(10)]
    opts = ThresholdOptions(require_min_rows=5)
    r = apply_threshold(_result(*changes), opts)
    assert not r.suppressed


def test_max_pct_added_suppresses():
    # 1 added out of 1 total = 100% > 50%
    opts = ThresholdOptions(max_pct_added=50.0)
    r = apply_threshold(_result(_added("a")), opts)
    assert r.suppressed


def test_max_pct_removed_suppresses():
    opts = ThresholdOptions(max_pct_removed=10.0)
    changes = [_removed(str(i)) for i in range(5)]
    r = apply_threshold(_result(*changes), opts)
    assert r.suppressed


# --- summary ---

def test_summary_suppressed():
    tr = ThresholdResult(suppressed=True)
    assert "suppressed" in tr.summary().lower()


def test_summary_not_suppressed():
    tr = ThresholdResult(kept=[_added("a")], dropped=[_modified("b")])
    s = tr.summary()
    assert "1" in s and "kept" in s
