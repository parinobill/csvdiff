"""Tests for csvdiff.exporter module."""

import json

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.exporter import export_csv, export_json, export_markdown


def _make_result(*changes):
    return DiffResult(changes=list(changes))


def _added(key, row):
    return RowChange(change_type="added", key=key, row=row, fields={})


def _removed(key, row):
    return RowChange(change_type="removed", key=key, row=row, fields={})


def _modified(key, fields):
    return RowChange(change_type="modified", key=key, row={}, fields=fields)


# --- export_json ---

def test_export_json_no_changes():
    data = json.loads(export_json(_make_result()))
    assert data["total"] == 0
    assert data["changes"] == []


def test_export_json_added_row():
    result = _make_result(_added("1", {"id": "1", "name": "Alice"}))
    data = json.loads(export_json(result))
    assert data["total"] == 1
    assert data["changes"][0]["change_type"] == "added"
    assert data["changes"][0]["name"] == "Alice"


def test_export_json_modified_row():
    result = _make_result(_modified("2", {"score": ("80", "95")}))
    data = json.loads(export_json(result))
    rec = data["changes"][0]
    assert rec["score_old"] == "80"
    assert rec["score_new"] == "95"


# --- export_csv ---

def test_export_csv_empty_result():
    assert export_csv(_make_result()) == ""


def test_export_csv_has_header():
    result = _make_result(_added("1", {"id": "1", "city": "NY"}))
    output = export_csv(result)
    lines = output.strip().splitlines()
    assert "change_type" in lines[0]
    assert "added" in lines[1]


def test_export_csv_removed_row():
    result = _make_result(_removed("3", {"id": "3", "city": "LA"}))
    output = export_csv(result)
    assert "removed" in output
    assert "LA" in output


# --- export_markdown ---

def test_export_markdown_no_changes():
    md = export_markdown(_make_result())
    assert "No changes" in md


def test_export_markdown_has_table():
    result = _make_result(_added("1", {"id": "1", "val": "x"}))
    md = export_markdown(result)
    assert "|" in md
    assert "change_type" in md
    assert "added" in md


def test_export_markdown_separator_row():
    result = _make_result(_added("1", {"id": "1"}))
    lines = export_markdown(result).strip().splitlines()
    assert "---" in lines[1]
