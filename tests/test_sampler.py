"""Tests for csvdiff.sampler."""

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.sampler import SampleOptions, sample_diff, sample_summary


def _added(key: str) -> RowChange:
    return RowChange(change_type="added", key=key, before={}, after={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(change_type="removed", key=key, before={"id": key}, after={})


def _modified(key: str) -> RowChange:
    return RowChange(
        change_type="modified",
        key=key,
        before={"id": key, "v": "1"},
        after={"id": key, "v": "2"},
    )


def _result(*changes: RowChange, unchanged: int = 0) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged=unchanged)


def test_sample_n_returns_correct_count():
    result = _result(*[_added(str(i)) for i in range(20)])
    opts = SampleOptions(n=5, seed=42)
    sampled = sample_diff(result, opts)
    assert len(sampled.changes) == 5


def test_sample_fraction_returns_correct_count():
    result = _result(*[_added(str(i)) for i in range(10)])
    opts = SampleOptions(fraction=0.4, seed=0)
    sampled = sample_diff(result, opts)
    assert len(sampled.changes) == 4


def test_sample_is_reproducible_with_seed():
    result = _result(*[_added(str(i)) for i in range(50)])
    opts = SampleOptions(n=10, seed=7)
    keys_a = [c.key for c in sample_diff(result, opts).changes]
    keys_b = [c.key for c in sample_diff(result, opts).changes]
    assert keys_a == keys_b


def test_sample_n_larger_than_pool_returns_all():
    result = _result(_added("a"), _added("b"))
    opts = SampleOptions(n=100, seed=1)
    sampled = sample_diff(result, opts)
    assert len(sampled.changes) == 2


def test_sample_filter_by_change_type():
    result = _result(_added("1"), _removed("2"), _modified("3"), _added("4"))
    opts = SampleOptions(n=10, change_types=["added"])
    sampled = sample_diff(result, opts)
    assert all(c.change_type == "added" for c in sampled.changes)
    assert len(sampled.changes) == 2


def test_sample_unchanged_preserved():
    result = _result(_added("x"), unchanged=99)
    opts = SampleOptions(n=1, seed=0)
    sampled = sample_diff(result, opts)
    assert sampled.unchanged == 99


def test_neither_n_nor_fraction_raises():
    result = _result(_added("a"))
    with pytest.raises(ValueError, match="Either"):
        sample_diff(result, SampleOptions())


def test_both_n_and_fraction_raises():
    result = _result(_added("a"))
    with pytest.raises(ValueError, match="only one"):
        sample_diff(result, SampleOptions(n=1, fraction=0.5))


def test_invalid_fraction_raises():
    result = _result(_added("a"))
    with pytest.raises(ValueError, match="fraction"):
        sample_diff(result, SampleOptions(fraction=1.5))


def test_summary_no_changes():
    result = _result(unchanged=5)
    sampled = _result(unchanged=5)
    msg = sample_summary(result, sampled)
    assert "No changes" in msg


def test_summary_shows_percentage():
    result = _result(*[_added(str(i)) for i in range(10)], unchanged=2)
    opts = SampleOptions(n=5, seed=3)
    sampled = sample_diff(result, opts)
    msg = sample_summary(result, sampled)
    assert "50.0%" in msg
    assert "5 of 10" in msg
