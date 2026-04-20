"""Tests for csvdiff.scorer."""

import pytest
from csvdiff.scorer import SimilarityScore, compute_score, score_as_dict
from csvdiff.differ import DiffResult, RowChange


def _make_result(*changes):
    return DiffResult(changes=list(changes))


def _added(key):
    return RowChange(key=key, change_type="added", old_row=None, new_row={"id": key})


def _removed(key):
    return RowChange(key=key, change_type="removed", old_row={"id": key}, new_row=None)


def _modified(key):
    return RowChange(
        key=key,
        change_type="modified",
        old_row={"id": key, "v": "a"},
        new_row={"id": key, "v": "b"},
    )


# --- SimilarityScore property tests ---

def test_score_all_unchanged():
    s = SimilarityScore(total_rows=10, unchanged_rows=10, added=0, removed=0, modified=0)
    assert s.score == 1.0
    assert s.percent == 100.0


def test_score_all_changed():
    s = SimilarityScore(total_rows=10, unchanged_rows=0, added=0, removed=10, modified=0)
    assert s.score == 0.0


def test_score_empty_files():
    s = SimilarityScore(total_rows=0, unchanged_rows=0, added=0, removed=0, modified=0)
    assert s.score == 1.0


def test_score_partial():
    s = SimilarityScore(total_rows=10, unchanged_rows=7, added=0, removed=3, modified=0)
    assert s.score == pytest.approx(0.7)
    assert s.percent == 70.0


def test_str_representation():
    s = SimilarityScore(total_rows=10, unchanged_rows=8, added=1, removed=1, modified=1)
    text = str(s)
    assert "80.0%" in text
    assert "+1" in text
    assert "-1" in text
    assert "~1" in text


# --- compute_score tests ---

def test_compute_score_no_changes():
    result = _make_result()
    score = compute_score(result, total_rows_in_old=5)
    assert score.score == 1.0
    assert score.unchanged_rows == 5
    assert score.total_rows == 5


def test_compute_score_all_removed():
    result = _make_result(_removed("1"), _removed("2"))
    score = compute_score(result, total_rows_in_old=2)
    assert score.removed == 2
    assert score.unchanged_rows == 0
    assert score.score == 0.0


def test_compute_score_with_additions():
    result = _make_result(_added("3"), _added("4"))
    score = compute_score(result, total_rows_in_old=3)
    assert score.added == 2
    assert score.total_rows == 5  # 3 old + 2 new
    assert score.unchanged_rows == 3


def test_compute_score_mixed():
    result = _make_result(_added("5"), _removed("1"), _modified("2"))
    score = compute_score(result, total_rows_in_old=4)
    assert score.added == 1
    assert score.removed == 1
    assert score.modified == 1
    assert score.unchanged_rows == 2  # 4 - 1 removed - 1 modified


def test_unchanged_never_negative():
    result = _make_result(_removed("1"), _removed("2"), _removed("3"))
    score = compute_score(result, total_rows_in_old=2)  # more removed than old (edge case)
    assert score.unchanged_rows >= 0


# --- score_as_dict tests ---

def test_score_as_dict_keys():
    result = _make_result()
    score = compute_score(result, total_rows_in_old=4)
    d = score_as_dict(score)
    assert set(d.keys()) == {"score", "percent", "total_rows", "unchanged_rows", "added", "removed", "modified"}


def test_score_as_dict_values():
    result = _make_result(_added("x"))
    score = compute_score(result, total_rows_in_old=3)
    d = score_as_dict(score)
    assert d["added"] == 1
    assert d["total_rows"] == 4
    assert 0.0 <= d["score"] <= 1.0
