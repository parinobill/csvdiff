"""Tests for csvdiff.ignorer."""
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.ignorer import IgnoreRules, apply_ignore, build_ignore_rules


def _make_result(*changes):
    return DiffResult(changes=list(changes), key_column="id")


def _modified(key, **fields):
    return RowChange(key=key, change_type="modified", field_changes={k: v for k, v in fields.items()})


def _added(key):
    return RowChange(key=key, change_type="added", field_changes={})


def _removed(key):
    return RowChange(key=key, change_type="removed", field_changes={})


def test_no_rules_returns_all_changes():
    result = _make_result(_added("1"), _removed("2"))
    out = apply_ignore(result, IgnoreRules())
    assert len(out.changes) == 2


def test_ignore_added_change_type():
    result = _make_result(_added("1"), _removed("2"))
    rules = build_ignore_rules(ignore_change_types=["added"])
    out = apply_ignore(result, rules)
    assert len(out.changes) == 1
    assert out.changes[0].change_type == "removed"


def test_ignore_removed_change_type():
    result = _make_result(_added("1"), _removed("2"), _modified("3", name=("a", "b")))
    rules = build_ignore_rules(ignore_change_types=["removed"])
    out = apply_ignore(result, rules)
    assert all(c.change_type != "removed" for c in out.changes)


def test_ignore_column_strips_field():
    change = _modified("1", name=("alice", "bob"), age=("30", "31"))
    result = _make_result(change)
    rules = build_ignore_rules(ignore_columns=["age"])
    out = apply_ignore(result, rules)
    assert len(out.changes) == 1
    assert "age" not in out.changes[0].field_changes
    assert "name" in out.changes[0].field_changes


def test_ignore_column_removes_row_when_no_fields_left():
    change = _modified("1", age=("30", "31"))
    result = _make_result(change)
    rules = build_ignore_rules(ignore_columns=["age"])
    out = apply_ignore(result, rules)
    assert len(out.changes) == 0


def test_ignore_row_by_pattern():
    result = _make_result(_added("test-123"), _added("prod-456"))
    rules = build_ignore_rules(ignore_row_pattern=r"^test-")
    out = apply_ignore(result, rules)
    assert len(out.changes) == 1
    assert out.changes[0].key == "prod-456"


def test_ignore_row_pattern_no_match_keeps_all():
    result = _make_result(_added("prod-1"), _added("prod-2"))
    rules = build_ignore_rules(ignore_row_pattern=r"^test-")
    out = apply_ignore(result, rules)
    assert len(out.changes) == 2


def test_build_ignore_rules_defaults():
    rules = build_ignore_rules()
    assert rules.columns == []
    assert rules.row_filter is None
    assert rules.change_types == []
