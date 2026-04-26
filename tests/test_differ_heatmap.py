"""Unit tests for csvdiff.differ_heatmap."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_heatmap import (
    DiffHeatmap,
    HeatmapCell,
    build_heatmap,
)


def _added(key: str, row: dict) -> RowChange:
    return RowChange(key=key, change_type="added", old_row=None, new_row=row, field_changes={})


def _removed(key: str, row: dict) -> RowChange:
    return RowChange(key=key, change_type="removed", old_row=row, new_row=None, field_changes={})


def _modified(key: str, field_changes: dict) -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        old_row={},
        new_row={},
        field_changes=field_changes,
    )


def _result(*changes) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged_count=0)


# --- DiffHeatmap unit tests ---

def test_empty_heatmap_returns_zero():
    hm = DiffHeatmap()
    assert hm.get("row1", "name") == 0


def test_increment_and_get():
    hm = DiffHeatmap()
    hm.increment("row1", "price")
    hm.increment("row1", "price")
    assert hm.get("row1", "price") == 2


def test_all_cells_sorted():
    hm = DiffHeatmap()
    hm.increment("b", "x")
    hm.increment("a", "y")
    cells = hm.all_cells()
    assert cells[0].row_key == "a"
    assert cells[1].row_key == "b"


def test_top_cells_limits_results():
    hm = DiffHeatmap()
    for i in range(10):
        hm.increment(f"row{i}", "f", i + 1)
    top = hm.top_cells(3)
    assert len(top) == 3
    assert top[0].change_count >= top[1].change_count


def test_hottest_field_single():
    hm = DiffHeatmap()
    hm.increment("r1", "price", 5)
    hm.increment("r2", "name", 1)
    assert hm.hottest_field() == "price"


def test_hottest_field_empty_returns_none():
    assert DiffHeatmap().hottest_field() is None


def test_summary_text():
    hm = DiffHeatmap()
    hm.increment("r1", "a", 3)
    hm.increment("r2", "b", 2)
    s = hm.summary()
    assert "5" in s
    assert "2" in s


# --- build_heatmap integration tests ---

def test_build_heatmap_modified():
    ch = _modified("1", {"price": ("10", "20"), "name": ("a", "a")})
    hm = build_heatmap(_result(ch))
    assert hm.get("1", "price") == 1
    # name did NOT change value, so should not be counted
    assert hm.get("1", "name") == 0


def test_build_heatmap_added():
    ch = _added("2", {"id": "2", "val": "x"})
    hm = build_heatmap(_result(ch))
    assert hm.get("2", "id") == 1
    assert hm.get("2", "val") == 1


def test_build_heatmap_removed():
    ch = _removed("3", {"id": "3", "score": "99"})
    hm = build_heatmap(_result(ch))
    assert hm.get("3", "score") == 1


def test_build_heatmap_empty_result():
    hm = build_heatmap(_result())
    assert hm.all_cells() == []
