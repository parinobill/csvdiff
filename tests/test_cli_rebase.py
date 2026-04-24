"""Integration tests for the rebase CLI sub-command."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace

from csvdiff.cli_rebase import cmd_rebase
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_patch import Patch
from csvdiff.patch_io import save_patch


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", before={}, after={"id": key})


def _modified(key: str) -> RowChange:
    return RowChange(
        key=key,
        change_type="modified",
        before={"id": key, "v": "old"},
        after={"id": key, "v": "new"},
    )


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _write_patch(path, *changes):
    p = Patch.from_diff_result(DiffResult(changes=list(changes)))
    save_patch(p, str(path))
    return str(path)


def test_no_conflicts_exits_zero(tmp):
    orig = _write_patch(tmp / "orig.json", _added("1"))
    up = _write_patch(tmp / "up.json", _added("2"))
    args = Namespace(
        original=orig,
        upstream=up,
        output=str(tmp / "out.json"),
        fail_on_conflicts=False,
    )
    assert cmd_rebase(args) == 0


def test_conflicts_with_flag_exits_two(tmp):
    orig = _write_patch(tmp / "orig.json", _modified("A"))
    up = _write_patch(tmp / "up.json", _modified("A"))
    args = Namespace(
        original=orig,
        upstream=up,
        output=str(tmp / "out.json"),
        fail_on_conflicts=True,
    )
    assert cmd_rebase(args) == 2


def test_conflicts_without_flag_exits_zero(tmp):
    orig = _write_patch(tmp / "orig.json", _modified("A"))
    up = _write_patch(tmp / "up.json", _modified("A"))
    args = Namespace(
        original=orig,
        upstream=up,
        output=str(tmp / "out.json"),
        fail_on_conflicts=False,
    )
    assert cmd_rebase(args) == 0


def test_missing_file_exits_one(tmp):
    args = Namespace(
        original=str(tmp / "missing.json"),
        upstream=str(tmp / "also_missing.json"),
        output=None,
        fail_on_conflicts=False,
    )
    assert cmd_rebase(args) == 1


def test_output_file_written(tmp):
    orig = _write_patch(tmp / "orig.json", _added("X"))
    up = _write_patch(tmp / "up.json", _added("Y"))
    out = str(tmp / "rebased.json")
    args = Namespace(
        original=orig, upstream=up, output=out, fail_on_conflicts=False
    )
    cmd_rebase(args)
    assert os.path.exists(out)
    with open(out) as f:
        data = json.load(f)
    assert "changes" in data
