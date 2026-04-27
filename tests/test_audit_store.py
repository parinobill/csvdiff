"""Tests for csvdiff.audit_store."""
import json
from pathlib import Path

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_audit import audit_result
from csvdiff.audit_store import (
    append_entry,
    entry_count,
    iter_entries,
    last_entry,
    load_entries,
)


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _result(n_added=0) -> DiffResult:
    changes = [
        RowChange(change_type="added", key=str(i), old_row={}, new_row={"id": str(i)})
        for i in range(n_added)
    ]
    return DiffResult(changes=changes)


def test_append_creates_file(tmp):
    p = tmp / "log.jsonl"
    append_entry(p, audit_result(_result()))
    assert p.exists()


def test_append_single_entry_parseable(tmp):
    p = tmp / "log.jsonl"
    append_entry(p, audit_result(_result(1), label="v1"))
    entries = load_entries(p)
    assert len(entries) == 1
    assert "audit" in entries[0]
    assert "patch" in entries[0]


def test_append_multiple_entries(tmp):
    p = tmp / "log.jsonl"
    for i in range(3):
        append_entry(p, audit_result(_result(i), label=f"run-{i}"))
    assert entry_count(p) == 3


def test_iter_entries_empty_when_file_missing(tmp):
    p = tmp / "nonexistent.jsonl"
    assert list(iter_entries(p)) == []


def test_last_entry_returns_most_recent(tmp):
    p = tmp / "log.jsonl"
    for i in range(4):
        append_entry(p, audit_result(_result(), label=f"run-{i}"))
    last = last_entry(p)
    assert last is not None
    assert last["audit"]["label"] == "run-3"


def test_last_entry_none_when_empty(tmp):
    p = tmp / "empty.jsonl"
    assert last_entry(p) is None


def test_entry_count_zero_when_missing(tmp):
    assert entry_count(tmp / "no.jsonl") == 0


def test_audit_label_preserved_in_store(tmp):
    p = tmp / "log.jsonl"
    append_entry(p, audit_result(_result(), label="my-label"))
    entries = load_entries(p)
    assert entries[0]["audit"]["label"] == "my-label"
