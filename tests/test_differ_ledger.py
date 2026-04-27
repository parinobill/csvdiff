"""Tests for csvdiff.differ_ledger."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_ledger import (
    Ledger,
    LedgerEntry,
    load_ledger,
    save_ledger,
)


def _rc(change_type: str, key: str = "k1") -> RowChange:
    return RowChange(key=key, change_type=change_type, old_row={}, new_row={})


def _result(*change_types: str) -> DiffResult:
    return DiffResult(changes=[_rc(ct, f"k{i}") for i, ct in enumerate(change_types)])


# --- LedgerEntry ---

def test_entry_total():
    e = LedgerEntry(label="run1", added=2, removed=1, modified=3)
    assert e.total == 6


def test_entry_str():
    e = LedgerEntry(label="run1", added=1, removed=2, modified=0)
    assert "run1" in str(e)
    assert "+1" in str(e)
    assert "-2" in str(e)


def test_entry_round_trip():
    e = LedgerEntry(label="x", added=1, removed=0, modified=2)
    assert LedgerEntry.from_dict(e.to_dict()) == e


# --- Ledger.record ---

def test_record_counts_correctly():
    ledger = Ledger()
    result = _result("added", "added", "removed", "modified")
    entry = ledger.record("run1", result)
    assert entry.added == 2
    assert entry.removed == 1
    assert entry.modified == 1
    assert len(ledger.entries) == 1


def test_record_empty_result():
    ledger = Ledger()
    entry = ledger.record("empty", DiffResult(changes=[]))
    assert entry.total == 0


def test_multiple_records_accumulate():
    ledger = Ledger()
    ledger.record("r1", _result("added"))
    ledger.record("r2", _result("removed", "modified"))
    totals = ledger.totals()
    assert totals.added == 1
    assert totals.removed == 1
    assert totals.modified == 1


# --- Ledger.summary ---

def test_summary_includes_total_line():
    ledger = Ledger()
    ledger.record("r1", _result("added"))
    s = ledger.summary()
    assert "TOTAL" in s
    assert "r1" in s


# --- save / load ---

def test_save_creates_file(tmp_path: Path):
    ledger = Ledger()
    ledger.record("r1", _result("added"))
    p = tmp_path / "ledger.json"
    save_ledger(ledger, p)
    assert p.exists()


def test_save_valid_json(tmp_path: Path):
    ledger = Ledger()
    ledger.record("r1", _result("modified"))
    p = tmp_path / "ledger.json"
    save_ledger(ledger, p)
    data = json.loads(p.read_text())
    assert isinstance(data, list)
    assert data[0]["label"] == "r1"


def test_load_roundtrip(tmp_path: Path):
    ledger = Ledger()
    ledger.record("r1", _result("added", "removed"))
    p = tmp_path / "ledger.json"
    save_ledger(ledger, p)
    loaded = load_ledger(p)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].label == "r1"
    assert loaded.entries[0].added == 1
    assert loaded.entries[0].removed == 1
