"""Tests for csvdiff.differ_watch_report."""
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_watch_report import (
    WatchReport,
    WatchReportEntry,
    build_watch_report,
)
from csvdiff.stats import compute_stats


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", old_row={}, new_row={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(key=key, change_type="removed", old_row={"id": key}, new_row={})


def _modified(key: str) -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        old_row={"id": key, "v": "1"},
        new_row={"id": key, "v": "2"},
    )


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged_count=0)


def test_build_watch_report_returns_empty():
    report = build_watch_report()
    assert isinstance(report, WatchReport)
    assert report.entries == []


def test_record_increments_cycle():
    report = build_watch_report()
    e1 = report.record(_result(_added("1")))
    e2 = report.record(_result(_added("2")))
    assert e1.cycle == 1
    assert e2.cycle == 2


def test_record_captures_stats():
    report = build_watch_report()
    entry = report.record(_result(_added("a"), _removed("b")))
    assert entry.stats.added == 1
    assert entry.stats.removed == 1


def test_latest_returns_none_when_empty():
    report = build_watch_report()
    assert report.latest() is None


def test_latest_returns_last_entry():
    report = build_watch_report()
    report.record(_result(_added("1")))
    e2 = report.record(_result(_added("2"), _added("3")))
    assert report.latest() is e2


def test_trend_vs_none_returns_tilde():
    report = build_watch_report()
    entry = report.record(_result(_added("1")))
    assert entry.trend_vs(None) == "~"


def test_trend_increasing():
    report = build_watch_report()
    e1 = report.record(_result(_added("1")))
    e2 = report.record(_result(_added("2"), _added("3")))
    assert e2.trend_vs(e1).startswith("+")


def test_trend_decreasing():
    report = build_watch_report()
    e1 = report.record(_result(_added("1"), _added("2")))
    e2 = report.record(_result(_added("3")))
    assert e2.trend_vs(e1).startswith("-")


def test_trend_equal():
    report = build_watch_report()
    e1 = report.record(_result(_added("1")))
    e2 = report.record(_result(_added("2")))
    assert e2.trend_vs(e1) == "="


def test_summary_no_cycles():
    report = build_watch_report()
    assert "No cycles" in report.summary()


def test_summary_includes_cycle_count():
    report = build_watch_report()
    report.record(_result(_added("1")))
    report.record(_result(_modified("2")))
    s = report.summary()
    assert "Cycles recorded: 2" in s


def test_entry_str_format():
    report = build_watch_report()
    entry = report.record(_result(_added("x"), _removed("y")))
    s = str(entry)
    assert "cycle 1" in s
    assert "added=1" in s
    assert "removed=1" in s
