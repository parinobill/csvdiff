"""Tests for csvdiff.differ_rank."""
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_rank import RankResult, RankedChange, rank_diff, _extract_score


def _modified(key: str, field: str, before: str, after: str) -> RowChange:
    return RowChange(
        change_type="modified",
        key=key,
        before={"id": key, field: before},
        after={"id": key, field: after},
    )


def _added(key: str, field: str, val: str) -> RowChange:
    return RowChange(
        change_type="added",
        key=key,
        before=None,
        after={"id": key, field: val},
    )


def _removed(key: str, field: str, val: str) -> RowChange:
    return RowChange(
        change_type="removed",
        key=key,
        before={"id": key, field: val},
        after=None,
    )


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


# --- _extract_score ---

def test_extract_score_modified_numeric():
    ch = _modified("1", "amount", "10", "25")
    assert _extract_score(ch, "amount") == pytest.approx(15.0)


def test_extract_score_added_uses_after():
    ch = _added("2", "amount", "42")
    assert _extract_score(ch, "amount") == pytest.approx(42.0)


def test_extract_score_removed_uses_before():
    ch = _removed("3", "amount", "7")
    assert _extract_score(ch, "amount") == pytest.approx(7.0)


def test_extract_score_non_numeric_returns_zero():
    ch = _modified("4", "name", "alice", "bob")
    assert _extract_score(ch, "name") == 0.0


def test_extract_score_missing_field_returns_zero():
    ch = _modified("5", "amount", "1", "2")
    assert _extract_score(ch, "nonexistent") == 0.0


# --- rank_diff ---

def test_rank_diff_orders_descending_by_default():
    result = _result(
        _modified("a", "score", "0", "5"),
        _modified("b", "score", "0", "100"),
        _modified("c", "score", "0", "20"),
    )
    rr = rank_diff(result, rank_field="score")
    keys = [rc.change.key for rc in rr.ranked]
    assert keys == ["b", "c", "a"]


def test_rank_diff_ascending():
    result = _result(
        _modified("a", "score", "0", "5"),
        _modified("b", "score", "0", "100"),
    )
    rr = rank_diff(result, rank_field="score", ascending=True)
    assert rr.ranked[0].change.key == "a"


def test_rank_diff_assigns_rank_integers():
    result = _result(
        _modified("x", "val", "1", "3"),
        _modified("y", "val", "1", "10"),
    )
    rr = rank_diff(result, rank_field="val")
    assert [rc.rank for rc in rr.ranked] == [1, 2]


def test_rank_diff_top_n_limits_top():
    result = _result(
        _modified("a", "v", "0", "1"),
        _modified("b", "v", "0", "2"),
        _modified("c", "v", "0", "3"),
    )
    rr = rank_diff(result, rank_field="v", top_n=2)
    assert len(rr.top()) == 2


def test_rank_diff_empty_result():
    rr = rank_diff(_result(), rank_field="amount")
    assert rr.ranked == []
    assert "No changes" in rr.summary()


def test_rank_diff_empty_field_raises():
    with pytest.raises(ValueError):
        rank_diff(_result(), rank_field="")


def test_summary_includes_rank_field():
    result = _result(_modified("1", "price", "10", "20"))
    rr = rank_diff(result, rank_field="price")
    assert "price" in rr.summary()


def test_ranked_change_str_contains_rank():
    ch = _modified("1", "v", "0", "5")
    rc = RankedChange(change=ch, rank=3, score=5.0)
    assert "#3" in str(rc)
