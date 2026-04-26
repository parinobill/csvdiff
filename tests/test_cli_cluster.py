"""Tests for csvdiff.cli_cluster."""
import argparse
import json
import pytest
from unittest.mock import patch, MagicMock

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_cluster import ClusterResult, ChangeCluster
from csvdiff.cli_cluster import add_cluster_args, cmd_cluster


def _make_args(**kwargs):
    defaults = dict(
        old="a.csv",
        new="b.csv",
        key="id",
        prefix_len=3,
        fmt="text",
        func=cmd_cluster,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _empty_result():
    return DiffResult(changes=[])


def _result_with_add():
    return DiffResult(
        changes=[
            RowChange(change_type="added", key_value="ABC001", row={"id": "ABC001"})
        ]
    )


def _make_cluster_result(empty=False):
    cr = ClusterResult()
    if not empty:
        c = ChangeCluster(label="ABC")
        c.changes.append(
            RowChange(change_type="added", key_value="ABC001", row={"id": "ABC001"})
        )
        cr.clusters["ABC"] = c
    return cr


def test_add_cluster_args_registers_subcommand():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    add_cluster_args(subs)
    args = parser.parse_args(["cluster", "a.csv", "b.csv", "--key", "id"])
    assert args.key == "id"
    assert args.prefix_len == 3


def test_cmd_cluster_no_changes_exits_zero(capsys):
    with patch("csvdiff.cli_cluster.run_pipeline", return_value=_empty_result()), \
         patch("csvdiff.cli_cluster.cluster_diff", return_value=_make_cluster_result(empty=True)):
        ret = cmd_cluster(_make_args())
    assert ret == 0


def test_cmd_cluster_with_changes_exits_one(capsys):
    with patch("csvdiff.cli_cluster.run_pipeline", return_value=_result_with_add()), \
         patch("csvdiff.cli_cluster.cluster_diff", return_value=_make_cluster_result()):
        ret = cmd_cluster(_make_args())
    assert ret == 1


def test_cmd_cluster_text_output_contains_label(capsys):
    with patch("csvdiff.cli_cluster.run_pipeline", return_value=_result_with_add()), \
         patch("csvdiff.cli_cluster.cluster_diff", return_value=_make_cluster_result()):
        cmd_cluster(_make_args(fmt="text"))
    out = capsys.readouterr().out
    assert "ABC" in out


def test_cmd_cluster_json_output_is_valid(capsys):
    with patch("csvdiff.cli_cluster.run_pipeline", return_value=_result_with_add()), \
         patch("csvdiff.cli_cluster.cluster_diff", return_value=_make_cluster_result()):
        cmd_cluster(_make_args(fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "clusters" in data
    assert "unclustered" in data


def test_cmd_cluster_json_cluster_has_count(capsys):
    with patch("csvdiff.cli_cluster.run_pipeline", return_value=_result_with_add()), \
         patch("csvdiff.cli_cluster.cluster_diff", return_value=_make_cluster_result()):
        cmd_cluster(_make_args(fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["clusters"]["ABC"]["count"] == 1
