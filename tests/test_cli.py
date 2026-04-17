"""Integration tests for the CLI entry point."""

import csv
import os
import tempfile
import pytest
from csvdiff.cli import main


def write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def test_no_diff_exits_zero(tmp_dir):
    fields = ["id", "name"]
    rows = [{"id": "1", "name": "Alice"}]
    old = str(tmp_dir / "old.csv")
    new = str(tmp_dir / "new.csv")
    write_csv(old, rows, fields)
    write_csv(new, rows, fields)
    assert main([old, new, "-k", "id", "--no-color"]) == 0


def test_diff_exits_one(tmp_dir):
    fields = ["id", "name"]
    old = str(tmp_dir / "old.csv")
    new = str(tmp_dir / "new.csv")
    write_csv(old, [{"id": "1", "name": "Alice"}], fields)
    write_csv(new, [{"id": "1", "name": "Bob"}], fields)
    assert main([old, new, "-k", "id", "--no-color"]) == 1


def test_missing_file_exits_one(tmp_dir):
    old = str(tmp_dir / "old.csv")
    new = str(tmp_dir / "missing.csv")
    write_csv(old, [{"id": "1", "name": "Alice"}], ["id", "name"])
    assert main([old, new, "-k", "id"]) == 1


def test_summary_flag(tmp_dir, capsys):
    fields = ["id", "name"]
    old = str(tmp_dir / "old.csv")
    new = str(tmp_dir / "new.csv")
    write_csv(old, [{"id": "1", "name": "Alice"}], fields)
    write_csv(new, [{"id": "2", "name": "Bob"}], fields)
    main([old, new, "-k", "id", "--no-color", "--summary"])
    captured = capsys.readouterr()
    assert "Summary:" in captured.out
