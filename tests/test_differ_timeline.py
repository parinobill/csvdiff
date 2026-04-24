"""Tests for csvdiff.differ_timeline."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_timeline import (
    RowTimeline,
    TimelineEntry,
    build_timeline,
    timeline_summary,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key: str, after: dict) -> RowChange:
    return RowChange(key_value=key, change_type="added", before=None, after=after)


def _removed(key: str, before: dict) -> RowChange:
    return RowChange(key_value=key, change_type="removed", before=before, after=None)


def _modified(key: str, before: dict, after: dict) -> RowChange:
    return RowChange(key_value=key, change_type="modified", before=before, after=after)


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


# ---------------------------------------------------------------------------
# TimelineEntry
# ---------------------------------------------------------------------------

def test_entry_str():
    e = TimelineEntry(label="v1", change_type="added", before=None, after={"name": "Alice"})
    assert "v1" in str(e)
    assert "added" in str(e)


# ---------------------------------------------------------------------------
# RowTimeline
# ---------------------------------------------------------------------------

def test_row_timeline_field_history_uses_after():
    tl = RowTimeline(key_value="1")
    tl.add(TimelineEntry("v1", "added", None, {"score": "10"}))
    tl.add(TimelineEntry("v2", "modified", {"score": "10"}, {"score": "20"}))
    assert tl.field_history("score") == ["10", "20"]


def test_row_timeline_field_history_falls_back_to_before():
    tl = RowTimeline(key_value="1")
    tl.add(TimelineEntry("v1", "removed", {"score": "5"}, None))
    assert tl.field_history("score") == ["5"]


def test_row_timeline_str_contains_key():
    tl = RowTimeline(key_value="abc")
    assert "abc" in str(tl)


# ---------------------------------------------------------------------------
# build_timeline
# ---------------------------------------------------------------------------

def test_build_timeline_empty():
    result = build_timeline([])
    assert result == {}


def test_build_timeline_single_result():
    r = _result(_added("1", {"name": "Alice"}))
    timelines = build_timeline([("v1", r)])
    assert "1" in timelines
    assert len(timelines["1"].entries) == 1
    assert timelines["1"].entries[0].label == "v1"
    assert timelines["1"].entries[0].change_type == "added"


def test_build_timeline_multiple_labels_same_key():
    r1 = _result(_added("42", {"val": "a"}))
    r2 = _result(_modified("42", {"val": "a"}, {"val": "b"}))
    r3 = _result(_removed("42", {"val": "b"}))
    timelines = build_timeline([("v1", r1), ("v2", r2), ("v3", r3)])
    tl = timelines["42"]
    assert len(tl.entries) == 3
    assert [e.change_type for e in tl.entries] == ["added", "modified", "removed"]


def test_build_timeline_different_keys_tracked_separately():
    r = _result(_added("1", {"x": "1"}), _added("2", {"x": "2"}))
    timelines = build_timeline([("v1", r)])
    assert set(timelines.keys()) == {"1", "2"}


def test_build_timeline_field_history_across_versions():
    r1 = _result(_added("7", {"price": "100"}))
    r2 = _result(_modified("7", {"price": "100"}, {"price": "150"}))
    timelines = build_timeline([("2023", r1), ("2024", r2)])
    assert timelines["7"].field_history("price") == ["100", "150"]


# ---------------------------------------------------------------------------
# timeline_summary
# ---------------------------------------------------------------------------

def test_timeline_summary_empty():
    assert "No timeline data" in timeline_summary({})


def test_timeline_summary_lists_keys():
    r = _result(_added("k1", {"a": "1"}), _removed("k2", {"a": "2"}))
    timelines = build_timeline([("v1", r)])
    summary = timeline_summary(timelines)
    assert "k1" in summary
    assert "k2" in summary
