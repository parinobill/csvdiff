"""Integration tests for csvdiff.cli_watch_report."""
import json
import os
import pytest

from csvdiff.cli_watch_report import cmd_watch_report


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _write_csv(path, rows):
    import csv
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _args(file_a, file_b, key="id", cycles=2, interval=0.0, fmt="text"):
    import argparse
    ns = argparse.Namespace(
        file_a=str(file_a),
        file_b=str(file_b),
        key=key,
        cycles=cycles,
        interval=interval,
        fmt=fmt,
    )
    return ns


def test_no_diff_exits_zero(tmp, capsys):
    rows = [{"id": "1", "val": "a"}, {"id": "2", "val": "b"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    _write_csv(a, rows)
    _write_csv(b, rows)
    rc = cmd_watch_report(_args(a, b))
    assert rc == 0


def test_diff_exits_one(tmp, capsys):
    a_rows = [{"id": "1", "val": "a"}]
    b_rows = [{"id": "1", "val": "CHANGED"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    _write_csv(a, a_rows)
    _write_csv(b, b_rows)
    rc = cmd_watch_report(_args(a, b))
    assert rc == 1


def test_json_output_structure(tmp, capsys):
    a_rows = [{"id": "1", "val": "x"}]
    b_rows = [{"id": "1", "val": "y"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    _write_csv(a, a_rows)
    _write_csv(b, b_rows)
    cmd_watch_report(_args(a, b, cycles=2, fmt="json"))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 2
    assert data[0]["cycle"] == 1
    assert "added" in data[0]
    assert "removed" in data[0]
    assert "modified" in data[0]


def test_missing_file_exits_one(tmp, capsys):
    a = tmp / "missing.csv"
    b = tmp / "also_missing.csv"
    rc = cmd_watch_report(_args(a, b))
    assert rc == 1


def test_text_output_contains_summary(tmp, capsys):
    rows = [{"id": "1", "val": "a"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    _write_csv(a, rows)
    _write_csv(b, rows)
    cmd_watch_report(_args(a, b, cycles=1, fmt="text"))
    captured = capsys.readouterr()
    assert "Watch report summary" in captured.out
    assert "Cycles recorded: 1" in captured.out
