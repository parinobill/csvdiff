"""Tests for csvdiff.cli_template."""

from __future__ import annotations

import csv
import io
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from csvdiff.cli_template import cmd_template


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _args(**kwargs):
    ns = MagicMock()
    ns.key = kwargs.get("key", "id")
    ns.fmt = kwargs.get("fmt", "text")
    ns.template_file = kwargs.get("template_file", None)
    ns.output = kwargs.get("output", None)
    ns.file_a = kwargs["file_a"]
    ns.file_b = kwargs["file_b"]
    return ns


def test_no_diff_exits_zero(tmp):
    rows = [{"id": "1", "name": "Alice"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    _write_csv(a, rows)
    _write_csv(b, rows)
    code = cmd_template(_args(file_a=str(a), file_b=str(b)))
    assert code == 0


def test_diff_exits_one(tmp):
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    _write_csv(a, [{"id": "1", "name": "Alice"}])
    _write_csv(b, [{"id": "1", "name": "Bob"}])
    code = cmd_template(_args(file_a=str(a), file_b=str(b)))
    assert code == 1


def test_missing_file_exits_one(tmp):
    a = tmp / "missing.csv"
    b = tmp / "b.csv"
    _write_csv(b, [{"id": "1"}])
    code = cmd_template(_args(file_a=str(a), file_b=str(b)))
    assert code == 1


def test_output_written_to_file(tmp):
    rows = [{"id": "1", "val": "x"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    out = tmp / "report.txt"
    _write_csv(a, rows)
    _write_csv(b, rows)
    cmd_template(_args(file_a=str(a), file_b=str(b), output=str(out)))
    assert out.exists()
    content = out.read_text()
    assert "Added" in content


def test_html_format(tmp):
    rows = [{"id": "1"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    _write_csv(a, rows)
    _write_csv(b, rows)
    out = tmp / "report.html"
    cmd_template(_args(file_a=str(a), file_b=str(b), fmt="html", output=str(out)))
    content = out.read_text()
    assert "<html>" in content


def test_custom_template_file(tmp):
    rows = [{"id": "1"}]
    a = tmp / "a.csv"
    b = tmp / "b.csv"
    tmpl_file = tmp / "tmpl.txt"
    _write_csv(a, rows)
    _write_csv(b, rows)
    tmpl_file.write_text("ADDED=$added REMOVED=$removed")
    out = tmp / "out.txt"
    cmd_template(
        _args(
            file_a=str(a),
            file_b=str(b),
            template_file=str(tmpl_file),
            output=str(out),
        )
    )
    content = out.read_text()
    assert "ADDED=0" in content
    assert "REMOVED=0" in content
