"""Tests for csvdiff.annotator."""

import pytest
from csvdiff.differ import RowChange, DiffResult
from csvdiff.annotator import AnnotatedChange, annotate_changes


def _make_result(*changes):
    return DiffResult(changes=list(changes))


def _added(key):
    return RowChange(key=key, change_type="added", before=None, after={"id": key})


def _removed(key):
    return RowChange(key=key, change_type="removed", before={"id": key}, after=None)


def _modified(key, field_changes=None):
    return RowChange(
        key=key,
        change_type="modified",
        before={"id": key, "v": "1"},
        after={"id": key, "v": "2"},
        field_changes=field_changes or {"v": ("1", "2")},
    )


def test_annotate_empty_result():
    result = _make_result()
    assert annotate_changes(result, "id") == []


def test_added_severity_is_info():
    result = _make_result(_added("1"))
    ann = annotate_changes(result, "id")
    assert ann[0].severity == "info"


def test_removed_severity_is_warning():
    result = _make_result(_removed("2"))
    ann = annotate_changes(result, "id")
    assert ann[0].severity == "warning"


def test_modified_severity_is_notice():
    result = _make_result(_modified("3"))
    ann = annotate_changes(result, "id")
    assert ann[0].severity == "notice"


def test_tags_include_change_type():
    result = _make_result(_added("1"))
    ann = annotate_changes(result, "id")
    assert "added" in ann[0].tags


def test_modified_tags_include_field_count():
    result = _make_result(_modified("3", {"a": ("x", "y"), "b": ("1", "2")}))
    ann = annotate_changes(result, "id")
    assert "fields:2" in ann[0].tags


def test_row_index_from_map():
    result = _make_result(_added("42"))
    ann = annotate_changes(result, "id", index_map={"42": 7})
    assert ann[0].row_index == 7


def test_row_index_none_when_no_map():
    result = _make_result(_added("1"))
    ann = annotate_changes(result, "id")
    assert ann[0].row_index is None


def test_str_includes_severity_and_key():
    result = _make_result(_removed("5"))
    ann = annotate_changes(result, "id")
    s = str(ann[0])
    assert "WARNING" in s


def test_returns_annotated_change_instances():
    result = _make_result(_added("1"), _removed("2"))
    ann = annotate_changes(result, "id")
    assert all(isinstance(a, AnnotatedChange) for a in ann)
    assert len(ann) == 2
