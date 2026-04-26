"""Integration tests for differ_cluster using a real DiffResult pipeline."""
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_cluster import cluster_diff, cluster_summary


def _rc(change_type, key):
    return RowChange(
        change_type=change_type,
        key_value=key,
        row={"id": key},
        old_row={"id": key} if change_type != "added" else None,
        changed_fields={"val": ("a", "b")} if change_type == "modified" else None,
    )


def _result(*changes):
    return DiffResult(changes=list(changes))


def test_mixed_types_same_prefix_grouped_together():
    result = _result(
        _rc("added", "US001"),
        _rc("removed", "US002"),
        _rc("modified", "US003"),
        _rc("added", "EU001"),
    )
    cr = cluster_diff(result, key_column="id", prefix_len=2)
    assert len(cr.clusters["US"]) == 3
    assert len(cr.clusters["EU"]) == 1
    assert sorted(cr.clusters["US"].change_types()) == ["added", "modified", "removed"]


def test_prefix_longer_than_key_uses_full_key():
    result = _result(_rc("added", "AB"))
    cr = cluster_diff(result, key_column="id", prefix_len=100)
    assert "AB" in cr.clusters


def test_cluster_summary_lists_all_clusters():
    result = _result(
        _rc("added", "AAA1"),
        _rc("removed", "BBB1"),
        _rc("modified", "CCC1"),
    )
    cr = cluster_diff(result, key_column="id", prefix_len=3)
    summary = cluster_summary(cr)
    assert "AAA" in summary
    assert "BBB" in summary
    assert "CCC" in summary
    assert "Total clusters: 3" in summary


def test_unclustered_not_counted_in_total_clustered():
    no_key = RowChange(change_type="added", key_value=None, row={})
    result = _result(_rc("added", "X01"), no_key)
    cr = cluster_diff(result, key_column="id", prefix_len=1)
    assert cr.total_clustered() == 1
    assert len(cr.unclustered) == 1
