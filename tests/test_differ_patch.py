"""Tests for csvdiff.differ_patch."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_patch import Patch, build_patch, apply_patch


def _result(*changes):
    return DiffResult(changes=list(changes))


def _added(row):
    return RowChange(change_type="added", old_row={}, new_row=row, field_changes={})


def _removed(row):
    return RowChange(change_type="removed", old_row=row, new_row={}, field_changes={})


def _modified(old, new, fields):
    return RowChange(change_type="modified", old_row=old, new_row=new, field_changes=fields)


ROWS = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob", "age": "25"},
    {"id": "3", "name": "Carol", "age": "40"},
]


def test_build_patch_addition():
    new_row = {"id": "4", "name": "Dave", "age": "22"}
    result = _result(_added(new_row))
    patch = build_patch(result, "id")
    assert patch.additions == [new_row]
    assert patch.removals == []
    assert patch.modifications == []


def test_build_patch_removal():
    result = _result(_removed({"id": "2", "name": "Bob", "age": "25"}))
    patch = build_patch(result, "id")
    assert patch.removals == ["2"]


def test_build_patch_modification():
    fields = {"age": {"old": "25", "new": "26"}}
    result = _result(_modified({"id": "2", "name": "Bob", "age": "25"},
                               {"id": "2", "name": "Bob", "age": "26"}, fields))
    patch = build_patch(result, "id")
    assert len(patch.modifications) == 1
    assert patch.modifications[0]["key"] == "2"
    assert patch.modifications[0]["fields"] == fields


def test_apply_patch_removes_row():
    patch = Patch(key_column="id", removals=["2"])
    result = apply_patch(ROWS, patch)
    ids = [r["id"] for r in result]
    assert "2" not in ids
    assert len(result) == 2


def test_apply_patch_adds_row():
    new_row = {"id": "4", "name": "Dave", "age": "22"}
    patch = Patch(key_column="id", additions=[new_row])
    result = apply_patch(ROWS, patch)
    assert any(r["id"] == "4" for r in result)


def test_apply_patch_modifies_row():
    patch = Patch(key_column="id", modifications=[
        {"key": "1", "fields": {"age": {"old": "30", "new": "31"}}}
    ])
    result = apply_patch(ROWS, patch)
    alice = next(r for r in result if r["id"] == "1")
    assert alice["age"] == "31"


def test_patch_roundtrip_json():
    patch = Patch(key_column="id", removals=["3"],
                  additions=[{"id": "5", "name": "Eve"}])
    restored = Patch.from_json(patch.to_json())
    assert restored.key_column == "id"
    assert restored.removals == ["3"]
    assert restored.additions == [{"id": "5", "name": "Eve"}]


def test_apply_patch_missing_removal_key_is_noop():
    patch = Patch(key_column="id", removals=["99"])
    result = apply_patch(ROWS, patch)
    assert len(result) == 3
