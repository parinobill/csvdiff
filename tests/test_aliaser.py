"""Tests for csvdiff.aliaser."""

from __future__ import annotations

import pytest

from csvdiff.aliaser import AliasMap, alias_diff, build_alias_map
from csvdiff.differ import DiffResult, RowChange


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _modified(key: str, old: dict, new: dict) -> RowChange:
    changed = [
        (col, old[col], new[col])
        for col in old
        if old.get(col) != new.get(col)
    ]
    return RowChange(change_type="modified", key=key, old_row=old, new_row=new, changed_fields=changed)


def _added(key: str, row: dict) -> RowChange:
    return RowChange(change_type="added", key=key, old_row=None, new_row=row, changed_fields=[])


def _removed(key: str, row: dict) -> RowChange:
    return RowChange(change_type="removed", key=key, old_row=row, new_row=None, changed_fields=[])


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes), unchanged_count=0)


# ---------------------------------------------------------------------------
# AliasMap
# ---------------------------------------------------------------------------

def test_display_known_column():
    am = AliasMap({"first_name": "First Name"})
    assert am.display("first_name") == "First Name"


def test_display_unknown_column_passthrough():
    am = AliasMap({"a": "A"})
    assert am.display("b") == "b"


def test_reverse_swaps_mapping():
    am = AliasMap({"col": "Column"})
    rev = am.reverse()
    assert rev.display("Column") == "col"
    assert rev.display("col") == "col"  # not in reversed map


def test_apply_to_dict_renames_keys():
    am = AliasMap({"id": "ID", "val": "Value"})
    result = am.apply_to_dict({"id": "1", "val": "x", "other": "y"})
    assert result == {"ID": "1", "Value": "x", "other": "y"}


# ---------------------------------------------------------------------------
# alias_diff
# ---------------------------------------------------------------------------

def test_alias_diff_renames_added_row():
    am = AliasMap({"first_name": "First"})
    r = _result(_added("1", {"first_name": "Alice"}))
    out = alias_diff(r, am)
    assert out.changes[0].new_row == {"First": "Alice"}


def test_alias_diff_renames_removed_row():
    am = AliasMap({"score": "Score"})    
    r = _result(_removed("2", {"score": "99"}))
    out = alias_diff(r, am)
    assert out.changes[0].old_row == {"Score": "99"}


def test_alias_diff_renames_changed_fields():
    am = AliasMap({"salary": "Salary"})
    r = _result(_modified("3", {"salary": "50k"}, {"salary": "60k"}))
    out = alias_diff(r, am)
    col, old, new = out.changes[0].changed_fields[0]
    assert col == "Salary"
    assert old == "50k"
    assert new == "60k"


def test_alias_diff_preserves_unchanged_count():
    am = AliasMap({"a": "A"})
    r = DiffResult(changes=[], unchanged_count=42)
    out = alias_diff(r, am)
    assert out.unchanged_count == 42


# ---------------------------------------------------------------------------
# build_alias_map
# ---------------------------------------------------------------------------

def test_build_alias_map_single():
    am = build_alias_map(["name:Full Name"])
    assert am.display("name") == "Full Name"


def test_build_alias_map_multiple():
    am = build_alias_map(["a:Alpha", "b:Beta"])
    assert am.display("a") == "Alpha"
    assert am.display("b") == "Beta"


def test_build_alias_map_strips_whitespace():
    am = build_alias_map([" col : Column "])
    assert am.display("col") == "Column"


def test_build_alias_map_missing_colon_raises():
    with pytest.raises(ValueError, match="expected 'original:alias'"):
        build_alias_map(["no-colon-here"])


def test_build_alias_map_empty_side_raises():
    with pytest.raises(ValueError, match="non-empty"):
        build_alias_map([":alias"])
