"""Tests for csvdiff.cli_blame."""
import json
import os
import textwrap
from unittest.mock import MagicMock, patch

import pytest

from csvdiff.cli_blame import _render_text, cmd_blame
from csvdiff.differ_blame import BlamedChange, BlameResult
from csvdiff.differ import RowChange


def _bc(label: str, ctype: str, key: str) -> BlamedChange:
    change = RowChange(
        change_type=ctype,
        key_value=key,
        before=None if ctype == "added" else {"id": key},
        after=None if ctype == "removed" else {"id": key},
    )
    return BlamedChange(change=change, source_label=label)


# ---------------------------------------------------------------------------
# _render_text
# ---------------------------------------------------------------------------


def test_render_text_no_changes():
    br = BlameResult(blamed=[])
    out = _render_text(br)
    assert "No changes" in out


def test_render_text_includes_label():
    br = BlameResult(blamed=[_bc("v1 → v2", "added", "10")])
    out = _render_text(br)
    assert "v1 → v2" in out


def test_render_text_includes_summary():
    br = BlameResult(blamed=[_bc("a → b", "removed", "5")])
    out = _render_text(br)
    assert "Blame summary" in out


# ---------------------------------------------------------------------------
# cmd_blame via mocked internals
# ---------------------------------------------------------------------------


def _make_args(files, key="id", as_json=False):
    args = MagicMock()
    args.files = files
    args.key = key
    args.json = as_json
    return args


def test_cmd_blame_too_few_files(capsys):
    rc = cmd_blame(_make_args(["only_one.csv"]))
    assert rc == 1
    captured = capsys.readouterr()
    assert "at least two" in captured.err


def test_cmd_blame_no_changes_returns_zero():
    empty_br = BlameResult(blamed=[])
    with patch("csvdiff.cli_blame._build_labeled_results", return_value=[]), \
         patch("csvdiff.cli_blame.blame_changes", return_value=empty_br):
        rc = cmd_blame(_make_args(["a.csv", "b.csv"]))
    assert rc == 0


def test_cmd_blame_with_changes_returns_one():
    br = BlameResult(blamed=[_bc("a → b", "added", "1")])
    with patch("csvdiff.cli_blame._build_labeled_results", return_value=[]), \
         patch("csvdiff.cli_blame.blame_changes", return_value=br):
        rc = cmd_blame(_make_args(["a.csv", "b.csv"]))
    assert rc == 1


def test_cmd_blame_json_output(capsys):
    br = BlameResult(blamed=[_bc("x → y", "modified", "99")])
    with patch("csvdiff.cli_blame._build_labeled_results", return_value=[]), \
         patch("csvdiff.cli_blame.blame_changes", return_value=br):
        cmd_blame(_make_args(["a.csv", "b.csv"], as_json=True))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["source"] == "x → y"
    assert data[0]["change_type"] == "modified"


def test_cmd_blame_file_not_found(capsys):
    with patch(
        "csvdiff.cli_blame._build_labeled_results",
        side_effect=FileNotFoundError("missing.csv not found"),
    ):
        rc = cmd_blame(_make_args(["a.csv", "b.csv"]))
    assert rc == 1
    assert "Error" in capsys.readouterr().err
