"""Integration tests: heatmap across multiple changes and edge cases."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_heatmap import build_heatmap


def _rc(key, change_type, old=None, new=None, fc=None):
    return RowChange(
        key=key,
        change_type=change_type,
        old_row=old or {},
        new_row=new or {},
        field_changes=fc or {},
    )


def _result(*changes):
    return DiffResult(changes=list(changes), unchanged_count=0)


def test_multiple_modifications_same_field_accumulate():
    """Two rows both modifying 'price' should give total count 2 across cells."""
    r1 = _rc("1", "modified", fc={"price": ("10", "20")})
    r2 = _rc("2", "modified", fc={"price": ("5", "7")})
    hm = build_heatmap(_result(r1, r2))
    assert hm.get("1", "price") == 1
    assert hm.get("2", "price") == 1
    assert hm.hottest_field() == "price"


def test_mixed_change_types_counted_separately():
    added = _rc("a", "added", new={"id": "a", "val": "x"})
    removed = _rc("b", "removed", old={"id": "b", "val": "y"})
    modified = _rc("c", "modified", fc={"val": ("1", "2")})
    hm = build_heatmap(_result(added, removed, modified))
    # added row: both fields counted
    assert hm.get("a", "id") == 1
    assert hm.get("a", "val") == 1
    # removed row: both fields counted
    assert hm.get("b", "val") == 1
    # modified row: only changed field
    assert hm.get("c", "val") == 1


def test_top_cells_returns_highest_first():
    changes = [
        _rc(f"row{i}", "modified", fc={"score": ("0", str(i))})
        for i in range(10)
    ]
    # Inflate row5 by adding it twice
    extra = _rc("row5", "modified", fc={"score": ("0", "99")})
    hm = build_heatmap(_result(*changes, extra))
    top = hm.top_cells(1)
    assert top[0].row_key == "row5"
    assert top[0].change_count == 2


def test_unchanged_field_not_in_heatmap():
    """A field_change entry where old == new must not appear in the heatmap."""
    ch = _rc("k", "modified", fc={"name": ("same", "same"), "price": ("1", "2")})
    hm = build_heatmap(_result(ch))
    assert hm.get("k", "name") == 0
    assert hm.get("k", "price") == 1


def test_empty_diff_result_produces_empty_heatmap():
    """An empty DiffResult should yield a heatmap with no entries."""
    hm = build_heatmap(_result())
    assert hm.top_cells(10) == []
    assert hm.hottest_field() is None
