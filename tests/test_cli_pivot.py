"""Tests for csvdiff.cli_pivot."""
import argparse
import types

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.cli_pivot import _render_text, _render_csv, cmd_pivot, add_pivot_args


def _added(key, row):
    return RowChange(key=key, change_type="added", old_row={}, new_row=row, changed_fields=[])


def _modified(key, old, new, fields):
    return RowChange(key=key, change_type="modified", old_row=old, new_row=new, changed_fields=fields)


def _result(**kw):
    return DiffResult(
        added=kw.get("added", []),
        removed=kw.get("removed", []),
        modified=kw.get("modified", []),
        unchanged=kw.get("unchanged", []),
    )


def _args(**kw):
    ns = argparse.Namespace()
    ns.top = kw.get("top", None)
    ns.pivot_format = kw.get("pivot_format", "text")
    return ns


def test_render_text_no_changes():
    from csvdiff.differ_pivot import FieldPivot
    assert _render_text([]) == "No field changes found."


def test_render_text_shows_field_summary():
    from csvdiff.differ_pivot import FieldPivot
    pv = FieldPivot(field_name="score", old_values=["80"], new_values=["90"])
    out = _render_text([pv])
    assert "score" in out
    assert "modified" in out


def test_render_csv_header():
    out = _render_csv([])
    assert out.startswith("field,added,removed,modified")


def test_render_csv_row():
    from csvdiff.differ_pivot import FieldPivot
    pv = FieldPivot(field_name="name", added_values=["Alice", "Bob"])
    out = _render_csv([pv])
    assert "name,2,0,0" in out


def test_cmd_pivot_no_changes_exits_zero(capsys):
    result = _result()
    code = cmd_pivot(_args(), result)
    assert code == 0


def test_cmd_pivot_with_changes_exits_one(capsys):
    result = _result(added=[_added("1", {"col": "val"})])
    code = cmd_pivot(_args(), result)
    assert code == 1


def test_cmd_pivot_csv_format_output(capsys):
    result = _result(added=[_added("1", {"x": "1"})])
    cmd_pivot(_args(pivot_format="csv"), result)
    captured = capsys.readouterr()
    assert "field,added,removed,modified" in captured.out


def test_add_pivot_args_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_pivot_args(sub)
    ns = parser.parse_args(["pivot", "--format", "csv"])
    assert ns.pivot_format == "csv"
    assert hasattr(ns, "pivot_func")
