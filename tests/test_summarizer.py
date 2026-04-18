"""Tests for csvdiff.summarizer module."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.stats import DiffStats
from csvdiff.summarizer import summarize, summarize_stats


def _change(ct: str, key: str = "k") -> RowChange:
    before = {"id": key} if ct != "added" else None
    after = {"id": key} if ct != "removed" else None
    return RowChange(key=key, change_type=ct, before=before, after=after, field_diffs={})


def _result(*types) -> DiffResult:
    return DiffResult(changes=[_change(t, str(i)) for i, t in enumerate(types)])


def test_no_changes_message():
    assert summarize(_result(), total_rows=5) == "No differences found."


def test_added_shown():
    msg = summarize(_result("added"), total_rows=4)
    assert "+ 1 added" in msg


def test_removed_shown():
    msg = summarize(_result("removed"), total_rows=4)
    assert "- 1 removed" in msg


def test_modified_shown():
    msg = summarize(_result("modified"), total_rows=4)
    assert "~ 1 modified" in msg


def test_verbose_shows_unchanged():
    msg = summarize(_result("added"), total_rows=5, verbose=True)
    assert "unchanged" in msg
    assert "Total rows" in msg


def test_non_verbose_hides_unchanged():
    msg = summarize(_result("added"), total_rows=5, verbose=False)
    assert "unchanged" not in msg


def test_percent_in_output():
    msg = summarize(_result("added"), total_rows=4)
    assert "%" in msg


def test_summarize_stats_no_changes():
    stats = DiffStats(added=0, removed=0, modified=0, unchanged=10, total_rows=10)
    assert summarize_stats(stats) == "No differences found."


def test_summarize_stats_with_changes():
    stats = DiffStats(added=2, removed=1, modified=3, unchanged=4, total_rows=10)
    msg = summarize_stats(stats)
    assert "+ 2 added" in msg
    assert "- 1 removed" in msg
    assert "~ 3 modified" in msg


def test_summarize_stats_verbose():
    stats = DiffStats(added=1, removed=0, modified=0, unchanged=9, total_rows=10)
    msg = summarize_stats(stats, verbose=True)
    assert "unchanged" in msg
