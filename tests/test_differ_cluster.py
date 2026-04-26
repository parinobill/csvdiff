"""Tests for csvdiff.differ_cluster."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_cluster import (
    ChangeCluster,
    ClusterResult,
    cluster_diff,
    cluster_summary,
)


def _added(key: str) -> RowChange:
    return RowChange(change_type="added", key_value=key, row={"id": key})


def _removed(key: str) -> RowChange:
    return RowChange(change_type="removed", key_value=key, row={"id": key})


def _modified(key: str) -> RowChange:
    return RowChange(
        change_type="modified",
        key_value=key,
        row={"id": key},
        old_row={"id": key, "v": "1"},
        changed_fields={"v": ("1", "2")},
    )


def _result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_empty_result_gives_empty_cluster():
    cr = cluster_diff(_result(), key_column="id")
    assert cr.clusters == {}
    assert cr.unclustered == []


def test_single_change_creates_one_cluster():
    cr = cluster_diff(_result(_added("ABC001")), key_column="id", prefix_len=3)
    assert "ABC" in cr.clusters
    assert len(cr.clusters["ABC"]) == 1


def test_two_changes_same_prefix_share_cluster():
    cr = cluster_diff(
        _result(_added("ABC001"), _modified("ABC002")),
        key_column="id",
        prefix_len=3,
    )
    assert len(cr.clusters) == 1
    assert len(cr.clusters["ABC"]) == 2


def test_different_prefixes_create_separate_clusters():
    cr = cluster_diff(
        _result(_added("ABC001"), _removed("XYZ999")),
        key_column="id",
        prefix_len=3,
    )
    assert set(cr.clusters.keys()) == {"ABC", "XYZ"}


def test_empty_key_value_goes_to_unclustered():
    change = RowChange(change_type="added", key_value="", row={})
    cr = cluster_diff(_result(change), key_column="id")
    assert len(cr.unclustered) == 1
    assert cr.clusters == {}


def test_total_clustered_counts_correctly():
    cr = cluster_diff(
        _result(_added("AA1"), _added("AA2"), _removed("BB1")),
        key_column="id",
        prefix_len=2,
    )
    assert cr.total_clustered() == 3


def test_change_types_returns_unique_types():
    cluster = ChangeCluster(label="X", changes=[_added("X1"), _added("X2"), _removed("X3")])
    assert sorted(cluster.change_types()) == ["added", "removed"]


def test_cluster_summary_contains_label():
    cr = cluster_diff(_result(_added("FOO1")), key_column="id", prefix_len=3)
    summary = cluster_summary(cr)
    assert "FOO" in summary
    assert "Total clusters: 1" in summary


def test_prefix_len_one_groups_by_first_char():
    cr = cluster_diff(
        _result(_added("Apple"), _added("Apricot"), _added("Banana")),
        key_column="id",
        prefix_len=1,
    )
    assert set(cr.clusters.keys()) == {"A", "B"}
    assert len(cr.clusters["A"]) == 2
