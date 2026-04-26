"""Tests for csvdiff.cli_heatmap."""
import json
import argparse
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.cli_heatmap import (
    cmd_heatmap,
    _render_text,
    _render_json,
    _render_csv,
    add_heatmap_args,
)
from csvdiff.differ_heatmap import build_heatmap


def _modified(key, field_changes):
    return RowChange(
        key=key, change_type="modified",
        old_row={}, new_row={}, field_changes=field_changes,
    )


def _result(*changes):
    return DiffResult(changes=list(changes), unchanged_count=0)


def _args(**kwargs):
    ns = argparse.Namespace(top=20, format="text")
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_render_text_no_changes():
    hm = build_heatmap(_result())
    out = _render_text([], hm)
    assert "No changes" in out


def test_render_text_shows_cell():
    ch = _modified("row1", {"price": ("1", "2")})
    hm = build_heatmap(_result(ch))
    cells = hm.all_cells()
    out = _render_text(cells, hm)
    assert "row1" in out
    assert "price" in out


def test_render_json_structure():
    ch = _modified("r1", {"x": ("a", "b")})
    hm = build_heatmap(_result(ch))
    cells = hm.all_cells()
    data = json.loads(_render_json(cells))
    assert isinstance(data, list)
    assert data[0]["row_key"] == "r1"
    assert data[0]["field"] == "x"
    assert data[0]["changes"] == 1


def test_render_csv_has_header():
    ch = _modified("r1", {"y": ("1", "2")})
    hm = build_heatmap(_result(ch))
    out = _render_csv(hm.all_cells())
    assert "row_key" in out
    assert "field" in out
    assert "changes" in out


def test_cmd_heatmap_text_returns_zero(capsys):
    ch = _modified("k1", {"f": ("old", "new")})
    result = _result(ch)
    rc = cmd_heatmap(_args(format="text"), result)
    assert rc == 0
    out = capsys.readouterr().out
    assert "k1" in out


def test_cmd_heatmap_json_returns_zero(capsys):
    ch = _modified("k2", {"g": ("a", "b")})
    result = _result(ch)
    rc = cmd_heatmap(_args(format="json"), result)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["row_key"] == "k2"


def test_add_heatmap_args_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_heatmap_args(sub)
    args = parser.parse_args(["heatmap", "--top", "5", "--format", "csv"])
    assert args.top == 5
    assert args.format == "csv"
