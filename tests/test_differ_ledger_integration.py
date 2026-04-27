"""Integration tests: ledger across multiple real DiffResult objects."""
from __future__ import annotations

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_ledger import Ledger


def _rc(ct: str, key: str) -> RowChange:
    return RowChange(key=key, change_type=ct, old_row={}, new_row={})


def _result(*pairs) -> DiffResult:
    return DiffResult(changes=[_rc(ct, k) for ct, k in pairs])


def test_ledger_totals_across_three_runs():
    ledger = Ledger()
    ledger.record("week1", _result(("added", "a1"), ("added", "a2")))
    ledger.record("week2", _result(("removed", "r1"), ("modified", "m1")))
    ledger.record("week3", _result(("modified", "m2"), ("modified", "m3"), ("added", "a3")))
    t = ledger.totals()
    assert t.added == 3
    assert t.removed == 1
    assert t.modified == 3
    assert t.total == 7


def test_summary_line_count_equals_entries_plus_total():
    ledger = Ledger()
    for i in range(4):
        ledger.record(f"run{i}", _result(("added", f"k{i}")))
    lines = ledger.summary().strip().splitlines()
    assert len(lines) == 5  # 4 entries + TOTAL


def test_empty_ledger_totals_are_zero():
    ledger = Ledger()
    t = ledger.totals()
    assert t.total == 0
    assert t.label == "TOTAL"


def test_single_run_totals_match_entry():
    ledger = Ledger()
    result = _result(("added", "a"), ("removed", "b"), ("removed", "c"))
    entry = ledger.record("only", result)
    t = ledger.totals()
    assert t.added == entry.added
    assert t.removed == entry.removed
    assert t.modified == entry.modified
