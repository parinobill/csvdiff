"""Tests for csvdiff.differ_blame."""
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_blame import (
    BlamedChange,
    BlameResult,
    blame_changes,
)


def _added(key: str) -> RowChange:
    return RowChange(change_type="added", key_value=key, before=None, after={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(change_type="removed", key_value=key, before={"id": key}, after=None)


def _modified(key: str) -> RowChange:
    return RowChange(
        change_type="modified",
        key_value=key,
        before={"id": key, "v": "1"},
        after={"id": key, "v": "2"},
    )


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


# ---------------------------------------------------------------------------


def test_blame_empty_inputs():
    result = blame_changes([])
    assert result.blamed == []


def test_blame_single_source():
    r = _result(_added("1"), _removed("2"))
    br = blame_changes([("v1", r)])
    assert len(br.blamed) == 2
    assert all(b.source_label == "v1" for b in br.blamed)


def test_blame_first_source_wins():
    """A change present in both results is attributed to the first."""
    change = _modified("42")
    r1 = _result(change)
    r2 = _result(change)
    br = blame_changes([("old", r1), ("new", r2)])
    assert len(br.blamed) == 1
    assert br.blamed[0].source_label == "old"


def test_blame_new_change_attributed_to_later_source():
    r1 = _result(_added("1"))
    r2 = _result(_added("1"), _added("2"))
    br = blame_changes([("v1", r1), ("v2", r2)])
    keys = {b.change.key_value: b.source_label for b in br.blamed}
    assert keys["1"] == "v1"
    assert keys["2"] == "v2"


def test_by_label_filters_correctly():
    r1 = _result(_added("A"))
    r2 = _result(_removed("B"))
    br = blame_changes([("alpha", r1), ("beta", r2)])
    assert len(br.by_label("alpha")) == 1
    assert len(br.by_label("beta")) == 1
    assert br.by_label("alpha")[0].change.key_value == "A"


def test_labels_order_preserved():
    r1 = _result(_added("1"))
    r2 = _result(_added("2"))
    r3 = _result(_added("3"))
    br = blame_changes([("x", r1), ("y", r2), ("z", r3)])
    assert br.labels() == ["x", "y", "z"]


def test_summary_no_changes():
    br = BlameResult(blamed=[])
    assert "No changes" in br.summary()


def test_summary_lists_labels():
    r1 = _result(_added("1"), _added("2"))
    r2 = _result(_removed("9"))
    br = blame_changes([("first", r1), ("second", r2)])
    s = br.summary()
    assert "first" in s
    assert "second" in s
    assert "2 change(s)" in s


def test_str_blamed_change():
    bc = BlamedChange(change=_added("99"), source_label="release-1")
    assert "release-1" in str(bc)
