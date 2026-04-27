"""Integration tests for the ledger CLI commands."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from csvdiff.cli_ledger import cmd_ledger
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_ledger import Ledger, LedgerEntry, save_ledger


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


@pytest.fixture()
def tmp(tmp_path: Path):
    return tmp_path


def _args(ledger_cmd, **kwargs):
    ns = MagicMock()
    ns.ledger_cmd = ledger_cmd
    ns.ledger_file = kwargs.get("ledger_file", "csvdiff.ledger.json")
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_record_creates_ledger(tmp: Path):
    old = tmp / "old.csv"
    new = tmp / "new.csv"
    _write_csv(old, [{"id": "1", "val": "a"}])
    _write_csv(new, [{"id": "1", "val": "b"}])
    lf = str(tmp / "ledger.json")
    args = _args("record", old=str(old), new=str(new), key="id", label="run1", ledger_file=lf)
    rc = cmd_ledger(args)
    assert rc == 0
    assert Path(lf).exists()


def test_record_appends_to_existing(tmp: Path):
    lf = tmp / "ledger.json"
    ledger = Ledger()
    ledger.entries.append(LedgerEntry("prior", 1, 0, 0))
    save_ledger(ledger, lf)

    old = tmp / "old.csv"
    new = tmp / "new.csv"
    _write_csv(old, [{"id": "1", "val": "a"}])
    _write_csv(new, [{"id": "1", "val": "b"}])
    args = _args("record", old=str(old), new=str(new), key="id", label="run2", ledger_file=str(lf))
    cmd_ledger(args)
    data = json.loads(lf.read_text())
    assert len(data) == 2


def test_show_missing_ledger_exits_one(tmp: Path, capsys):
    args = _args("show", ledger_file=str(tmp / "missing.json"))
    rc = cmd_ledger(args)
    assert rc == 1


def test_show_prints_summary(tmp: Path, capsys):
    lf = tmp / "ledger.json"
    ledger = Ledger()
    ledger.entries.append(LedgerEntry("run1", 2, 1, 0))
    save_ledger(ledger, lf)
    args = _args("show", ledger_file=str(lf))
    rc = cmd_ledger(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "run1" in out
    assert "TOTAL" in out
