"""Tests for csvdiff CLI including column filter flags."""
import os
import csv
import pytest
from csvdiff.cli import main


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def test_no_diff_exits_zero(tmp_dir):
    rows = [{"id": "1", "name": "Alice"}]
    a = str(tmp_dir / "a.csv")
    b = str(tmp_dir / "b.csv")
    write_csv(a, rows)
    write_csv(b, rows)
    assert main([a, b, "--key", "id"]) == 0


def test_diff_exits_one(tmp_dir):
    a = str(tmp_dir / "a.csv")
    b = str(tmp_dir / "b.csv")
    write_csv(a, [{"id": "1", "name": "Alice"}])
    write_csv(b, [{"id": "1", "name": "Bob"}])
    assert main([a, b, "--key", "id"]) == 1


def test_missing_file_exits_one(tmp_dir):
    a = str(tmp_dir / "a.csv")
    write_csv(a, [{"id": "1", "name": "Alice"}])
    assert main([a, str(tmp_dir / "missing.csv"), "--key", "id"]) == 1


def test_include_columns_ignores_others(tmp_dir):
    a = str(tmp_dir / "a.csv")
    b = str(tmp_dir / "b.csv")
    write_csv(a, [{"id": "1", "name": "Alice", "age": "30"}])
    write_csv(b, [{"id": "1", "name": "Alice", "age": "99"}])
    # age differs but we only include id and name — should be no diff
    assert main([a, b, "--key", "id", "--include-columns", "id", "name"]) == 0


def test_exclude_columns_ignores_field(tmp_dir):
    a = str(tmp_dir / "a.csv")
    b = str(tmp_dir / "b.csv")
    write_csv(a, [{"id": "1", "name": "Alice", "age": "30"}])
    write_csv(b, [{"id": "1", "name": "Alice", "age": "99"}])
    assert main([a, b, "--key", "id", "--exclude-columns", "age"]) == 0
