"""Integration-style tests for cli_baseline sub-commands."""

import json
import csv as _csv
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from csvdiff.differ import DiffResult, RowChange
from csvdiff import cli_baseline as clb


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _make_result(*changes: RowChange) -> DiffResult:
    return DiffResult(key_column="id", changes=list(changes))


def _added(key: str) -> RowChange:
    return RowChange(key=key, change_type="added", old_row=None, new_row={"id": key})


# ---------------------------------------------------------------------------
# cmd_save_baseline
# ---------------------------------------------------------------------------

def test_save_writes_file(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    out = tmp_path / "baseline.json"
    _write_csv(old, [{"id": "1", "v": "a"}])
    _write_csv(new, [{"id": "1", "v": "a"}, {"id": "2", "v": "b"}])

    args = MagicMock(old=str(old), new=str(new), key="id", output=str(out))

    with patch("csvdiff.cli_baseline.read_csv") as mock_read, \
         patch("csvdiff.cli_baseline.compute_diff") as mock_diff:
        mock_read.side_effect = [{"1": {"id": "1", "v": "a"}},
                                  {"1": {"id": "1", "v": "a"}, "2": {"id": "2", "v": "b"}}]
        mock_diff.return_value = _make_result(_added("2"))
        rc = clb.cmd_save_baseline(args)

    assert rc == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["key_column"] == "id"


# ---------------------------------------------------------------------------
# cmd_compare_baseline
# ---------------------------------------------------------------------------

def test_compare_no_new_returns_zero(tmp_path, capsys):
    from csvdiff.baseline import save_baseline

    base_path = tmp_path / "base.json"
    base_result = _make_result(_added("1"))
    save_baseline(base_result, base_path)

    args = MagicMock(old="a.csv", new="b.csv", key="id",
                     baseline=str(base_path), no_color=True)

    with patch("csvdiff.cli_baseline.read_csv") as mock_read, \
         patch("csvdiff.cli_baseline.compute_diff") as mock_diff:
        mock_read.side_effect = [{}, {}]
        mock_diff.return_value = _make_result(_added("1"))  # same as baseline
        rc = clb.cmd_compare_baseline(args)

    assert rc == 0
    captured = capsys.readouterr()
    assert "No changes" in captured.out


def test_compare_new_changes_returns_one(tmp_path, capsys):
    from csvdiff.baseline import save_baseline

    base_path = tmp_path / "base.json"
    save_baseline(_make_result(), base_path)  # empty baseline

    args = MagicMock(old="a.csv", new="b.csv", key="id",
                     baseline=str(base_path), no_color=True)

    with patch("csvdiff.cli_baseline.read_csv") as mock_read, \
         patch("csvdiff.cli_baseline.compute_diff") as mock_diff, \
         patch("csvdiff.cli_baseline.format_diff", return_value="(diff)"):
        mock_read.side_effect = [{}, {}]
        mock_diff.return_value = _make_result(_added("99"))
        rc = clb.cmd_compare_baseline(args)

    assert rc == 1
